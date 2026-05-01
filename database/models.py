from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./gestionmed_bot.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    """Estado de conversación de cada usuario de Instagram."""
    __tablename__ = "conversations"

    instagram_id = Column(String, primary_key=True, index=True)
    state = Column(String, default="MENU")          # estado actual del flujo
    temp_data = Column(Text, default="{}")          # JSON con datos temporales de la cita
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Appointment(Base):
    """Citas (auditorías gratuitas) agendadas."""
    __tablename__ = "appointments"

    id = Column(String, primary_key=True)           # UUID
    instagram_id = Column(String, index=True)
    name = Column(String)
    phone = Column(String)
    clinic_type = Column(String)                    # dental | fisio | estetica | otra
    preferred_date = Column(String)                 # dd/mm/yyyy
    preferred_time = Column(String)                 # HH:MM
    notes = Column(Text, default="")
    confirmed_at = Column(DateTime, default=datetime.utcnow)
    review_sent = Column(Boolean, default=False)    # si ya se envió solicitud de reseña
    review_scheduled_at = Column(DateTime, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
