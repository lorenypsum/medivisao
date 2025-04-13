from sqlalchemy import Column, String, ForeignKey, Float, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    user_picture = Column(Text, nullable=True)

    imagens = relationship("Imagem", back_populates="usuario", cascade="all, delete-orphan")

class Imagem(Base):
    __tablename__ = "imagens"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, ForeignKey("usuarios.id"))
    original = Column(Text)
    histogram = Column(Text)
    resize = Column(Text)
    normalize = Column(Text)
    gaussian = Column(Text)
    clahe = Column(Text)
    otsu = Column(Text)
    morphological = Column(Text)
    edge = Column(Text)
    resultado_final = Column(Text)
    diagnostico = Column(String)
    probabilidade = Column(Float)
    metadados = Column(Text)

    data = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="imagens")

