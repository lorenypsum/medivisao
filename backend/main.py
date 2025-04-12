from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List


import models, schemas, crud
from database import SessionLocal, engine, Base

# Cria as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS para frontend em HTML + PyScript
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste para seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependência de sessão com banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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



