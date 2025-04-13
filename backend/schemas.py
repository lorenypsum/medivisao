from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UsuarioBase(BaseModel):
    name: str
    username: str
    user_picture: Optional[str] = None
    email: str
    password: Optional[str] = None

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id: str
    name: str
    username: str
    user_picture: Optional[str] = None

    class Config:
        orm_mode = True

class ImagemBase(BaseModel):
    usuario_id: str
    original: Optional[str] = None
    resize: Optional[str] = None
    normalize: Optional[str] = None
    histogram: Optional[str] = None
    gaussian: Optional[str] = None
    clahe: Optional[str] = None
    otsu: Optional[str] = None
    morphological: Optional[str] = None
    edge: Optional[str] = None
    resultado_final: Optional[str] = None
    diagnostico: Optional[str] = None
    probabilidade: Optional[float] = None
    metadados: Optional[str] = None

class ImagemCreate(ImagemBase):
    usuario_id: str

class ImagemResponse(ImagemBase):
    id: str
    usuario_id: str
    original: Optional[str]
    resultado_final: Optional[str]
    metadados: Optional[str]
    diagnostico: Optional[str]
    probabilidade: Optional[float]
    data: datetime

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True
