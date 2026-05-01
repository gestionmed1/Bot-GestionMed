# GestionMed Instagram Chatbot — Guía de Configuración

## ¿Qué hace este bot?
- Responde preguntas frecuentes sobre GestionMed en Instagram DM
- Agenda auditorías gratuitas de 30 minutos paso a paso
- Envía automáticamente un mensaje de solicitud de reseña en Google 1 hora después de cada auditoría

---

## Requisitos previos
- Python 3.11+
- Cuenta de Instagram **Business o Creator** (no vale personal)
- Página de **Facebook** vinculada a esa cuenta de Instagram
- Cuenta en [Meta for Developers](https://developers.facebook.com)
- Un servidor con **HTTPS** para el webhook (p.ej. Railway, Render, VPS con Nginx + Let's Encrypt)

---

## Paso 1 — Instalar dependencias

```bash
cd chatbot-gestionmed
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

---

## Paso 2 — Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus datos reales (ver detalle abajo).

### Cómo obtener el PAGE_ACCESS_TOKEN

1. Ve a [developers.facebook.com](https://developers.facebook.com)
2. Crea una App de tipo **Business**
3. En el panel izquierdo: **Instagram > Configuración de Instagram**
4. Conecta tu página de Facebook + cuenta de Instagram Business
5. Ve a **Herramientas > Explorador de la API Graph**
6. Genera un token con estos permisos:
   - `instagram_manage_messages`
   - `pages_messaging`
   - `pages_read_engagement`
7. Copia el token en `PAGE_ACCESS_TOKEN`

### Cómo obtener el PAGE_ID

```
https://graph.facebook.com/me?access_token=TU_TOKEN
```
El campo `id` es tu `PAGE_ID`.

### Cómo obtener la URL de reseña de Google

1. Ve a [Google Business Profile](https://business.google.com)
2. Selecciona tu negocio
3. Haz clic en **Pedir reseñas**
4. Copia el enlace corto (tipo `https://g.page/r/.../review`)
5. Pégalo en `GOOGLE_REVIEW_URL`

---

## Paso 3 — Configurar el Webhook en Meta Developer

1. En tu App de Meta, ve a **Instagram > Webhooks**
2. URL del webhook: `https://TU-DOMINIO.com/webhook`
3. Token de verificación: el mismo que pusiste en `.env` → `WEBHOOK_VERIFY_TOKEN`
4. Suscríbete al campo: **messages**
5. Meta llamará a tu servidor GET /webhook para verificar → asegúrate de que el servidor esté corriendo

---

## Paso 4 — Arrancar el bot

```bash
python app.py
```

O con uvicorn directamente:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Verifica que funciona:
```
GET https://TU-DOMINIO.com/health
→ {"status": "ok", "service": "GestionMed Instagram Bot"}
```

---

## Paso 5 — Despliegue en producción (Railway recomendado)

### Con Railway (gratis para empezar)

1. Crea cuenta en [railway.app](https://railway.app)
2. Nuevo proyecto → **Deploy from GitHub**
3. Sube el código a un repo GitHub
4. En Railway: **Variables** → añade todas las del `.env`
5. Railway te da una URL HTTPS automáticamente
6. Usa esa URL como webhook en Meta Developer

### Con Render (alternativa gratuita)

1. [render.com](https://render.com) → New Web Service
2. Conecta tu repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Añade las variables de entorno

---

## Flujo de conversación

```
Usuario escribe → Bot responde
─────────────────────────────────────────────────────
"hola" / "menu"          → Menú principal
"1"                      → Lista de servicios
"2"                      → Información de precios
"3" / "cita" / "agendar" → Inicia flujo de cita
"4" / "contacto"         → Datos de contacto
[cualquier pregunta]     → Búsqueda por palabras clave

Flujo de cita:
  Nombre → Tipo clínica → Fecha → Hora → Teléfono → Confirmar
  ↓
  Cita guardada en BD + solicitud de reseña programada

1 hora después de la cita:
  Bot envía mensaje de solicitud de reseña en Google
```

---

## Estructura del proyecto

```
chatbot-gestionmed/
├── app.py                    # Servidor FastAPI + webhooks
├── config.py                 # Variables de entorno
├── requirements.txt
├── .env.example
├── bot/
│   ├── handler.py            # Orquestador de mensajes
│   ├── faq.py                # Preguntas frecuentes + palabras clave
│   ├── appointment.py        # Flujo de agendado de citas
│   └── instagram.py          # Cliente de la API de Instagram
├── database/
│   └── models.py             # Modelos SQLite (conversaciones + citas)
└── scheduler/
    └── review_sender.py      # Job automático de solicitud de reseñas
```

---

## Personalizar respuestas

- **FAQs**: edita `bot/faq.py` → sección `FAQS` y `KEYWORD_MAP`
- **Mensaje de bienvenida**: edita `MENU_TEXT` en `bot/faq.py`
- **Mensaje de reseña**: edita `REVIEW_MSG` en `scheduler/review_sender.py`
- **Horario de atención**: edita `_validate_time()` en `bot/appointment.py`

---

## Soporte
Si tienes dudas con la configuración: grupogestionmed@outlook.com | 671 464 362
