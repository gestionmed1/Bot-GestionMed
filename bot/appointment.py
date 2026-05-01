"""Flujo de agendado de auditoría gratuita."""

import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import Conversation, Appointment

# ── Estados del flujo de cita ──────────────────────────────────────────────
STATE_MENU = "MENU"
STATE_BOOKING_NAME = "BOOKING_NAME"
STATE_BOOKING_CLINIC = "BOOKING_CLINIC"
STATE_BOOKING_DATE = "BOOKING_DATE"
STATE_BOOKING_TIME = "BOOKING_TIME"
STATE_BOOKING_PHONE = "BOOKING_PHONE"
STATE_BOOKING_CONFIRM = "BOOKING_CONFIRM"
STATE_DONE = "DONE"

CLINIC_OPTIONS = {
    "1": "dental",
    "2": "fisioterapia",
    "3": "estetica",
    "4": "otra",
    "dental": "dental",
    "fisio": "fisioterapia",
    "fisioterapia": "fisioterapia",
    "estética": "estetica",
    "estetica": "estetica",
    "otra": "otra",
}

# ── Mensajes del flujo ─────────────────────────────────────────────────────
MSG_START = (
    "¡Perfecto! Vamos a reservar tu *auditoría gratuita de 30 minutos* 🎉\n\n"
    "Es completamente sin compromiso. Solo necesito unos datos rápidos.\n\n"
    "¿Cuál es tu nombre completo?"
)

MSG_ASK_CLINIC = (
    "Encantado/a, {name} 😊\n\n"
    "¿Qué tipo de clínica tienes?\n\n"
    "1️⃣ Dental\n"
    "2️⃣ Fisioterapia\n"
    "3️⃣ Estética\n"
    "4️⃣ Otra\n\n"
    "Responde con el número o el nombre."
)

MSG_ASK_DATE = (
    "Perfecto 👍\n\n"
    "¿Qué día prefieres para la auditoría?\n"
    "Escribe la fecha en formato *dd/mm/aaaa* (ej: 15/05/2025)"
)

MSG_ASK_TIME = (
    "¡Anotado! ¿A qué hora te va mejor?\n"
    "Nuestro horario es de *9:00 a 19:00* (lunes a viernes)\n\n"
    "Escribe la hora en formato *HH:MM* (ej: 10:30)"
)

MSG_ASK_PHONE = (
    "Casi listo 🙌\n\n"
    "¿Cuál es tu número de teléfono o WhatsApp para confirmar la cita?"
)

MSG_CONFIRM = (
    "✅ *Resumen de tu auditoría gratuita:*\n\n"
    "👤 Nombre: {name}\n"
    "🏥 Clínica: {clinic_type}\n"
    "📅 Fecha: {preferred_date}\n"
    "🕐 Hora: {preferred_time}\n"
    "📱 Teléfono: {phone}\n\n"
    "¿Confirmas la cita? Responde *SÍ* para confirmar o *NO* para empezar de nuevo."
)

MSG_CONFIRMED = (
    "🎉 ¡Cita confirmada!\n\n"
    "Te contactaremos al {phone} para recordarte la auditoría el {preferred_date} a las {preferred_time}.\n\n"
    "Si necesitas cambiarla, escríbenos aquí o llámanos al 671 464 362.\n\n"
    "¡Hasta pronto! 😊"
)

MSG_CANCELLED = (
    "Sin problema. Puedes empezar de nuevo cuando quieras.\n"
    "Escribe *CITA* o *MENU* para volver al inicio."
)

MSG_INVALID_DATE = (
    "❌ Esa fecha no parece válida. Por favor usa el formato *dd/mm/aaaa*\n"
    "Ejemplo: 20/05/2025"
)

MSG_INVALID_TIME = (
    "❌ Esa hora no parece válida. Por favor usa el formato *HH:MM*\n"
    "Ejemplo: 10:30\n"
    "Horario disponible: 9:00 a 19:00 (lunes a viernes)"
)

MSG_INVALID_CLINIC = (
    "Por favor elige una de las opciones:\n"
    "1 - Dental\n2 - Fisioterapia\n3 - Estética\n4 - Otra"
)


# ── Helpers ────────────────────────────────────────────────────────────────

def _load_temp(conv: Conversation) -> dict:
    try:
        return json.loads(conv.temp_data or "{}")
    except Exception:
        return {}


def _save_temp(conv: Conversation, data: dict):
    conv.temp_data = json.dumps(data, ensure_ascii=False)


def _validate_date(text: str) -> bool:
    try:
        dt = datetime.strptime(text.strip(), "%d/%m/%Y")
        return dt.date() >= datetime.utcnow().date()
    except ValueError:
        return False


def _validate_time(text: str) -> bool:
    try:
        t = datetime.strptime(text.strip(), "%H:%M").time()
        return 9 <= t.hour <= 18
    except ValueError:
        return False


# ── Procesador principal del flujo ────────────────────────────────────────

def process_booking(instagram_id: str, text: str, db: Session) -> str:
    """
    Maneja el flujo completo de agendado.
    Devuelve el mensaje de respuesta a enviar al usuario.
    """
    conv = db.get(Conversation, instagram_id)
    if conv is None:
        conv = Conversation(instagram_id=instagram_id, state=STATE_MENU, temp_data="{}")
        db.add(conv)

    state = conv.state
    text_clean = text.strip()

    # Entrada al flujo de cita desde cualquier estado
    if text_clean.upper() in ("CITA", "AGENDAR", "RESERVAR", "3") and state == STATE_MENU:
        conv.state = STATE_BOOKING_NAME
        _save_temp(conv, {})
        db.commit()
        return MSG_START

    if state == STATE_BOOKING_NAME:
        if len(text_clean) < 2:
            return "Por favor dime tu nombre completo 😊"
        data = _load_temp(conv)
        data["name"] = text_clean.title()
        _save_temp(conv, data)
        conv.state = STATE_BOOKING_CLINIC
        db.commit()
        return MSG_ASK_CLINIC.format(name=data["name"])

    if state == STATE_BOOKING_CLINIC:
        choice = CLINIC_OPTIONS.get(text_clean.lower())
        if not choice:
            return MSG_INVALID_CLINIC
        data = _load_temp(conv)
        data["clinic_type"] = choice
        _save_temp(conv, data)
        conv.state = STATE_BOOKING_DATE
        db.commit()
        return MSG_ASK_DATE

    if state == STATE_BOOKING_DATE:
        if not _validate_date(text_clean):
            return MSG_INVALID_DATE
        data = _load_temp(conv)
        data["preferred_date"] = text_clean.strip()
        _save_temp(conv, data)
        conv.state = STATE_BOOKING_TIME
        db.commit()
        return MSG_ASK_TIME

    if state == STATE_BOOKING_TIME:
        if not _validate_time(text_clean):
            return MSG_INVALID_TIME
        data = _load_temp(conv)
        data["preferred_time"] = text_clean.strip()
        _save_temp(conv, data)
        conv.state = STATE_BOOKING_PHONE
        db.commit()
        return MSG_ASK_PHONE

    if state == STATE_BOOKING_PHONE:
        if len(text_clean) < 9:
            return "Por favor introduce un número de teléfono válido (mínimo 9 dígitos)."
        data = _load_temp(conv)
        data["phone"] = text_clean
        _save_temp(conv, data)
        conv.state = STATE_BOOKING_CONFIRM
        db.commit()
        return MSG_CONFIRM.format(**data)

    if state == STATE_BOOKING_CONFIRM:
        if text_clean.upper() in ("SÍ", "SI", "S", "YES", "CONFIRMAR", "OK", "SÍ"):
            data = _load_temp(conv)
            appointment = Appointment(
                id=str(uuid.uuid4()),
                instagram_id=instagram_id,
                name=data.get("name", ""),
                phone=data.get("phone", ""),
                clinic_type=data.get("clinic_type", ""),
                preferred_date=data.get("preferred_date", ""),
                preferred_time=data.get("preferred_time", ""),
                confirmed_at=datetime.utcnow(),
                review_scheduled_at=_parse_review_time(
                    data.get("preferred_date", ""), data.get("preferred_time", "")
                ),
            )
            db.add(appointment)
            conv.state = STATE_MENU
            _save_temp(conv, {})
            db.commit()
            try:
                from bot.email_sender import send_appointment_email
                send_appointment_email(data)
            except Exception as e:
                import logging
                logging.getLogger(__name__).error("Error email: %s", e)
            return MSG_CONFIRMED.format(**data)

        elif text_clean.upper() in ("NO", "N", "CANCELAR"):
            conv.state = STATE_MENU
            _save_temp(conv, {})
            db.commit()
            return MSG_CANCELLED

        else:
            return "Responde *SÍ* para confirmar o *NO* para cancelar."

    # Estado desconocido: reset al menú
    conv.state = STATE_MENU
    db.commit()
    return None  # el caller manejará el menú principal


def _parse_review_time(date_str: str, time_str: str) -> datetime | None:
    """Calcula cuándo enviar la solicitud de reseña (1 hora después de la cita)."""
    try:
        dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
        return dt + timedelta(hours=1)
    except Exception:
        return None


def is_in_booking_flow(state: str) -> bool:
    return state in (
        STATE_BOOKING_NAME,
        STATE_BOOKING_CLINIC,
        STATE_BOOKING_DATE,
        STATE_BOOKING_TIME,
        STATE_BOOKING_PHONE,
        STATE_BOOKING_CONFIRM,
    )
