from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Meta / Instagram ──────────────────────────────────────────────────
    # Token de página de Facebook con permisos de Instagram Messaging
    PAGE_ACCESS_TOKEN: str = ""

    # Token de verificación del webhook (tú lo inventas, debe coincidir con Meta Developer)
    WEBHOOK_VERIFY_TOKEN: str = "gestionmed_webhook_2025"

    # ID de la página de Facebook vinculada a la cuenta de Instagram Business
    PAGE_ID: str = ""

    # ── URLs externas ─────────────────────────────────────────────────────
    # URL directa para dejar reseña en Google (desde Google Business Profile)
    GOOGLE_REVIEW_URL: str = "https://g.page/r/XXXXXXXX/review"

    # ── App ───────────────────────────────────────────────────────────────
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
