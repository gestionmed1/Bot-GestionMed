import httpx
import logging
from config import settings

logger = logging.getLogger(__name__)

GRAPH_API = "https://graph.facebook.com/v19.0"


async def send_message(recipient_id: str, text: str) -> bool:
    """Envía un mensaje de texto por Instagram DM."""
    url = f"{GRAPH_API}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE",
    }
    headers = {"Authorization": f"Bearer {settings.PAGE_ACCESS_TOKEN}"}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            logger.error("Instagram API error %s: %s", e.response.status_code, e.response.text)
            return False
        except Exception as e:
            logger.error("Error enviando mensaje: %s", e)
            return False


async def send_quick_replies(recipient_id: str, text: str, replies: list[dict]) -> bool:
    """Envía un mensaje con opciones de respuesta rápida."""
    url = f"{GRAPH_API}/me/messages"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "text": text,
            "quick_replies": replies,
        },
        "messaging_type": "RESPONSE",
    }
    headers = {"Authorization": f"Bearer {settings.PAGE_ACCESS_TOKEN}"}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            return True
        except Exception as e:
            logger.error("Error enviando quick replies: %s", e)
            return False


def make_quick_reply(title: str, payload: str) -> dict:
    return {"content_type": "text", "title": title, "payload": payload}
