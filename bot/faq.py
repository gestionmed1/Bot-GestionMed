"""Respuestas a preguntas frecuentes sobre GestionMed."""

FAQS: dict[str, str] = {
    "servicios": (
        "🏥 *GestionMed* ofrece 4 servicios clave para clínicas:\n\n"
        "1️⃣ *Chatbot 24/7* (WhatsApp/Instagram) — Gestiona citas y responde dudas automáticamente\n"
        "2️⃣ *Dashboard de Facturación* — Ve tus ingresos, ocupación y proyecciones en tiempo real\n"
        "3️⃣ *Web + SEO Local* — Página optimizada para aparecer en Google y convertir visitas en pacientes\n"
        "4️⃣ *Gestión de Reseñas* — Solicita reseñas automáticamente tras cada cita y filtra valoraciones negativas\n\n"
        "¿Te gustaría saber más de alguno? 👇"
    ),
    "precio": (
        "💰 Nuestros planes no tienen permanencia — puedes cancelar con 30 días de aviso.\n\n"
        "El precio exacto depende de los servicios que necesites para tu clínica.\n"
        "Lo mejor es que hagas una *auditoría gratuita de 30 minutos* (sin compromiso) para que te demos un presupuesto personalizado.\n\n"
        "¿Te la agendamos ahora? Responde *CITA* 😊"
    ),
    "tiempo": (
        "⚡ Implementamos todo en *14 días*.\n\n"
        "Desde que firmas, en 2 semanas ya tienes el sistema funcionando en tu clínica."
    ),
    "clientes": (
        "🏆 Ya trabajamos con *+50 clínicas* en España con una valoración media de *4.9/5 estrellas*.\n\n"
        "Nos especializamos en clínicas dentales, centros de fisioterapia y clínicas de estética."
    ),
    "especialidades": (
        "🦷 Trabajamos con clínicas de:\n\n"
        "• Odontología / Dental\n"
        "• Fisioterapia\n"
        "• Medicina Estética\n\n"
        "Si tu clínica es de otro tipo, consúltanos igualmente — seguramente podemos ayudarte."
    ),
    "contacto": (
        "📞 Puedes contactarnos por:\n\n"
        "• 📱 *Teléfono/WhatsApp*: 671 464 362\n"
        "• 📧 *Email*: grupogestionmed@outlook.com\n"
        "• 🌐 *Web*: gestionmed.es\n\n"
        "O si prefieres, agendamos una *auditoría gratuita* respondiendo *CITA* 😊"
    ),
    "auditoria": (
        "🎁 La *Auditoría Gratuita* es una videollamada de 30 minutos donde:\n\n"
        "✅ Analizamos la situación actual de tu clínica\n"
        "✅ Identificamos cuántos pacientes y facturación estás perdiendo\n"
        "✅ Te presentamos un plan personalizado sin compromiso\n\n"
        "Solo hay *10 plazas disponibles* este mes.\n"
        "Responde *CITA* para reservar la tuya."
    ),
    "permanencia": (
        "✅ *Sin permanencia*.\n\n"
        "Puedes cancelar en cualquier momento con solo 30 días de aviso. Sin letras pequeñas ni penalizaciones."
    ),
    "zona": (
        "📍 Trabajamos con clínicas en toda *España*. Todo el proceso es online, así que la ubicación no es ningún problema."
    ),
}

KEYWORD_MAP: dict[str, str] = {
    "servicio": "servicios",
    "precio": "precio",
    "coste": "precio",
    "cuanto": "precio",
    "cuánto": "precio",
    "tarifa": "precio",
    "tiempo": "tiempo",
    "implementa": "tiempo",
    "días": "tiempo",
    "dias": "tiempo",
    "cliente": "clientes",
    "referencia": "clientes",
    "experiencia": "clientes",
    "dental": "especialidades",
    "fisio": "especialidades",
    "estética": "especialidades",
    "estetica": "especialidades",
    "especialidad": "especialidades",
    "contacto": "contacto",
    "telefono": "contacto",
    "teléfono": "contacto",
    "email": "contacto",
    "whatsapp": "contacto",
    "auditoría": "auditoria",
    "auditoria": "auditoria",
    "gratis": "auditoria",
    "gratuita": "auditoria",
    "permanencia": "permanencia",
    "contrato": "permanencia",
    "cancelar": "permanencia",
    "zona": "zona",
    "españa": "zona",
    "ciudad": "zona",
    "ubicación": "zona",
}


def get_faq_response(text: str) -> str | None:
    """Busca una respuesta FAQ basada en palabras clave del mensaje."""
    text_lower = text.lower().strip()
    for keyword, topic in KEYWORD_MAP.items():
        if keyword in text_lower:
            return FAQS.get(topic)
    return None


MENU_TEXT = (
    "👋 ¡Hola! Soy el asistente virtual de *GestionMed*.\n\n"
    "Ayudamos a clínicas dentales, de fisioterapia y estética a automatizar su gestión y atraer más pacientes.\n\n"
    "¿En qué puedo ayudarte hoy?\n\n"
    "1️⃣ Ver nuestros servicios\n"
    "2️⃣ Información de precios\n"
    "3️⃣ Agendar auditoría gratuita\n"
    "4️⃣ Hablar con el equipo\n\n"
    "Escribe el número o tu pregunta directamente 😊"
)

FALLBACK_TEXT = (
    "Hmm, no estoy seguro de cómo responderte eso 🤔\n\n"
    "Pero puedo ayudarte con:\n"
    "• *servicios* — qué hacemos\n"
    "• *precio* — cuánto cuesta\n"
    "• *CITA* — agendar auditoría gratuita\n"
    "• *contacto* — hablar con el equipo\n\n"
    "¿Qué prefieres?"
)
