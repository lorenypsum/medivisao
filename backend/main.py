from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import models, schemas, crud
from database import SessionLocal, engine, Base

from processamento import (
    Resize,
    Normalize,
    GaussianBlur,
    CLAHE_Color,
    OtsuThreshold,
    HistogramEqualization,
    MorphologicalTransform,
    EdgeDetection,
)

# Cria as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependência de sessão com banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CORS para frontend em HTML + PyScript
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste para seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de requisição
class ProcessRequest(BaseModel):
    image_base64: str
    method: str  # resize, normalize, gaussian, clahe, otsu, histogram, morphological, edge

# Decode da imagem em base64 para OpenCV
def decode_image(base64_string):
    try:
        header, encoded = base64_string.split(",", 1)
        data = base64.b64decode(encoded)
        np_arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao decodificar imagem: {e}")

# Encode da imagem OpenCV para base64
def encode_image(img):
    _, buffer = cv2.imencode(".png", img)
    b64 = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/png;base64,{b64}"

# Rota para processar a imagem
@app.post("/processar")
def processar_imagem(req: ProcessRequest):
    img = decode_image(req.image_base64)

    try:
        if req.method == "resize":
            result = Resize((128, 128)).fit_transform([img])[0]
        elif req.method == "histogram":
            result = HistogramEqualization().fit_transform([img])[0]
            result = (result * 255).astype(np.uint8)
        elif req.method == "normalize":
            result = Normalize().fit_transform([img])[0]
            result = (result * 255).astype(np.uint8)
        elif req.method == "gaussian":
            result = GaussianBlur().fit_transform([img])[0]
        elif req.method == "clahe":
            result = CLAHE_Color().fit_transform([img])[0]
        elif req.method == "otsu":
            result = OtsuThreshold().fit_transform([img])[0]
        elif req.method == "morphological":
            result = MorphologicalTransform().fit_transform([img])[0]
        elif req.method == "edge":
            result = EdgeDetection().fit_transform([img])[0]        
        else:
            raise ValueError("Filtro inválido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"processed_image": encode_image(result)}

@app.post("/imagens", response_model=schemas.ImagemResponse)
def salvar_ou_atualizar(imagem: schemas.ImagemCreate, db: Session = Depends(get_db)):
    return crud.salvar_ou_atualizar_imagem(db, imagem)

@app.post("/usuarios", response_model=schemas.UsuarioResponse)
def criar_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    existing = crud.get_usuario_por_username(db, usuario.username)
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    return crud.criar_usuario(db, usuario)


@app.get("/usuarios", response_model=list[schemas.UsuarioResponse])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.listar_usuarios(db, skip=skip, limit=limit)


@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
def obter_usuario(usuario_id: str, db: Session = Depends(get_db)):
    usuario = crud.get_usuario_por_username(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: str, db: Session = Depends(get_db)):
    success = crud.deletar_usuario(db, usuario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"ok": True}


@app.post("/imagens", response_model=schemas.ImagemResponse)
def salvar_imagem(imagem: schemas.ImagemCreate, db: Session = Depends(get_db)):
    return crud.criar_imagem(db, imagem)


@app.get("/usuarios/{usuario_id}/imagens", response_model=List[schemas.ImagemResponse])
def listar_imagens(usuario_id: str, db: Session = Depends(get_db)):
    return crud.listar_imagens_do_usuario(db, usuario_id)


@app.delete("/imagens/{imagem_id}")
def deletar(imagem_id: str, db: Session = Depends(get_db)):
    success = crud.deletar_imagem(db, imagem_id)
    if not success:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return {"ok": True}

@app.get("/usuarios/{usuario_id}/imagem", response_model=schemas.ImagemResponse)
def obter_imagem(usuario_id: str, db: Session = Depends(get_db)):
    imagem = (
        db.query(models.Imagem).filter(models.Imagem.usuario_id == usuario_id).first()
    )
    if not imagem:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return imagem
