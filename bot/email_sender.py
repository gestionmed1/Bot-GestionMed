import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

logger = logging.getLogger(__name__)


def send_appointment_email(data: dict):
    """Envía un email de notificación cuando se confirma una nueva cita."""
    if not settings.EMAIL_PASSWORD:
        logger.warning("EMAIL_PASSWORD no configurado, no se envía email.")
        return

    subject = f"📅 Nueva cita agendada — {data.get('name', '')} ({data.get('preferred_date', '')})"

    body = f"""
Nueva auditoría gratuita agendada en GestionMed.

👤 Nombre:     {data.get('name', '')}
🏥 Clínica:    {data.get('clinic_type', '')}
📅 Fecha:      {data.get('preferred_date', '')}
🕐 Hora:       {data.get('preferred_time', '')}
📱 Teléfono:   {data.get('phone', '')}

---
Mensaje enviado automáticamente por el chatbot de Instagram de GestionMed.
"""

    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = settings.EMAIL_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.office365.com", 587, timeout=10) as server:
            server.starttls()
            server.login(settings.EMAIL_FROM, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, settings.EMAIL_TO, msg.as_string())
        logger.info("Email de cita enviado a %s", settings.EMAIL_TO)
    except Exception as e:
        logger.error("Error enviando email de cita: %s", e)
