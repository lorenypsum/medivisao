from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UsuarioBase(BaseModel):
    name: str
    username: str

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id: str
    user_picture: Optional[str] = None

    class Config:
        orm_mode = True

class ImagemBase(BaseModel):
    original: str
    resize: Optional[str]
    normalize: Optional[str]
    gaussian: Optional[str]
    clahe: Optional[str]
    otsu: Optional[str]
    resultado_final: Optional[str]
    diagnostico: Optional[str]
    probabilidade: Optional[float]
    metadados: Optional[str]

class ImagemCreate(ImagemBase):
    usuario_id: str

class ImagemResponse(ImagemBase):
    id: str
    data: datetime

    class Config:
        orm_mode = True
