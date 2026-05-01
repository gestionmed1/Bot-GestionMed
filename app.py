"""
Servidor principal del chatbot de Instagram para GestionMed.
Recibe webhooks de Meta y responde a los mensajes de Instagram DM.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException, Depends
from sqlalchemy.orm import Session

from config import settings
from database.models import init_db, get_db
from bot.handler import handle_message
from bot.instagram import send_message
from scheduler.review_sender import create_scheduler

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = create_scheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    scheduler.start()
    logger.info("GestionMed Bot iniciado. Scheduler activo.")
    yield
    scheduler.shutdown()
    logger.info("Bot detenido.")


app = FastAPI(title="GestionMed Instagram Bot", lifespan=lifespan)


# ── Webhook verification (GET) ─────────────────────────────────────────────
@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Meta llama a este endpoint para verificar el webhook.
    Debe devolver el hub.challenge si el token coincide.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verificado por Meta.")
        return Response(content=challenge, media_type="text/plain")

    logger.warning("Intento de verificación fallido. Token: %s", token)
    raise HTTPException(status_code=403, detail="Token inválido")


# ── Webhook receiver (POST) ────────────────────────────────────────────────
@app.post("/webhook")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    """Recibe eventos de Instagram Messaging y procesa los mensajes entrantes."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    if body.get("object") != "instagram":
        return {"status": "ignored"}

    for entry in body.get("entry", []):
        for event in entry.get("messaging", []):
            await _process_event(event, db)

    return {"status": "ok"}


async def _process_event(event: dict, db: Session):
    """Procesa un evento individual de mensajería."""
    sender_id = event.get("sender", {}).get("id")
    if not sender_id:
        return

    # Ignorar mensajes enviados por la propia página
    recipient_id = event.get("recipient", {}).get("id")
    if sender_id == settings.PAGE_ID:
        return

    message = event.get("message", {})
    if not message:
        return

    # Ignorar mensajes eco (copies de lo que envía la página)
    if message.get("is_echo"):
        return

    text = message.get("text", "").strip()
    if not text:
        return

    logger.info("Mensaje de %s: %s", sender_id, text[:80])

    response_text = await handle_message(sender_id, text, db)
    if response_text:
        await send_message(sender_id, response_text)


# ── Health check ───────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "GestionMed Instagram Bot"}


# ── Entrypoint ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=False,
    )
