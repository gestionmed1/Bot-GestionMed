"""Orquestador principal: decide qué responder a cada mensaje entrante."""

import logging
from sqlalchemy.orm import Session
from database.models import Conversation
from bot.faq import get_faq_response, MENU_TEXT, FALLBACK_TEXT
from bot.appointment import process_booking, is_in_booking_flow, STATE_MENU

logger = logging.getLogger(__name__)

MENU_TRIGGERS = {"menu", "inicio", "hola", "hi", "hello", "start", "empezar", "0"}
CITA_TRIGGERS = {"cita", "agendar", "reservar", "auditoría", "auditoria", "3"}
MENU_OPTION_MAP = {
    "1": "servicios",
    "2": "precio",
    "4": "contacto",
}

from bot.faq import FAQS


async def handle_message(instagram_id: str, text: str, db: Session) -> str:
    """
    Procesa un mensaje entrante y devuelve el texto de respuesta.
    Retorna None si no hay nada que responder (no debería ocurrir).
    """
    text_clean = text.strip()
    text_lower = text_clean.lower()

    # Obtener o crear conversación
    conv = db.get(Conversation, instagram_id)
    if conv is None:
        conv = Conversation(instagram_id=instagram_id, state=STATE_MENU)
        db.add(conv)
        db.commit()

    state = conv.state

    # ── Si el usuario está en medio de agendar una cita, continuar ese flujo
    if is_in_booking_flow(state):
        # Permitir salida del flujo con "menu" o "cancelar"
        if text_lower in ("menu", "cancelar", "inicio", "salir"):
            conv.state = STATE_MENU
            db.commit()
            return MENU_TEXT
        return process_booking(instagram_id, text_clean, db)

    # ── Menú principal ─────────────────────────────────────────────────────

    # Saludo / reset al menú
    if text_lower in MENU_TRIGGERS:
        return MENU_TEXT

    # Disparador de cita
    if text_lower in CITA_TRIGGERS:
        return process_booking(instagram_id, "3", db)

    # Opciones numéricas del menú (1, 2, 4)
    if text_clean in MENU_OPTION_MAP:
        topic = MENU_OPTION_MAP[text_clean]
        return FAQS[topic]

    # Búsqueda por palabras clave en FAQs
    faq_response = get_faq_response(text_clean)
    if faq_response:
        return faq_response

    # Fallback
    return FALLBACK_TEXT
