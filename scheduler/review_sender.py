"""
Scheduler que revisa cada minuto si hay citas cuya hora ya pasó
y envía la solicitud de reseña de Google por Instagram DM.
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from database.models import Appointment, SessionLocal
from bot.instagram import send_message
from config import settings

logger = logging.getLogger(__name__)

REVIEW_MSG = (
    "¡Hola {name}! 👋\n\n"
    "Espero que nuestra auditoría de hoy haya sido de gran ayuda para tu clínica.\n\n"
    "¿Te ha parecido útil? Nos alegraría mucho que dejaras una reseña en Google, "
    "¡nos ayuda a llegar a más clínicas como la tuya! 🙏\n\n"
    "👉 {google_review_url}\n\n"
    "¡Muchas gracias y hasta pronto! 😊\n"
    "— Equipo GestionMed"
)


async def send_pending_reviews():
    """Busca citas pendientes de reseña y envía el mensaje."""
    db: Session = SessionLocal()
    try:
        now = datetime.utcnow()
        pending = (
            db.query(Appointment)
            .filter(
                Appointment.review_sent == False,
                Appointment.review_scheduled_at != None,
                Appointment.review_scheduled_at <= now,
            )
            .all()
        )

        for appt in pending:
            msg = REVIEW_MSG.format(
                name=appt.name.split()[0],  # solo el primer nombre
                google_review_url=settings.GOOGLE_REVIEW_URL,
            )
            success = await send_message(appt.instagram_id, msg)
            if success:
                appt.review_sent = True
                db.commit()
                logger.info("Reseña enviada a %s (cita %s)", appt.instagram_id, appt.id)
            else:
                logger.warning("No se pudo enviar reseña a %s", appt.instagram_id)

    except Exception as e:
        logger.error("Error en send_pending_reviews: %s", e)
    finally:
        db.close()


def create_scheduler() -> AsyncIOScheduler:
    """Crea y configura el scheduler de reseñas."""
    scheduler = AsyncIOScheduler(timezone="Europe/Madrid")
    scheduler.add_job(
        send_pending_reviews,
        trigger="interval",
        minutes=1,
        id="review_sender",
        replace_existing=True,
    )
    return scheduler
