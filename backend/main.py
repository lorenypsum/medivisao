from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import cv2
import numpy as np
import base64
import models, schemas, crud
from database import SessionLocal, engine, Base
import shutil
import os
from tensorflow import keras
from sklearn.pipeline import Pipeline

from processamento import (
    Resize,
    Normalize,
    GaussianBlur,
    CLAHE_Color,
    OtsuThreshold,
    HistogramEqualization,
    MorphologicalTransform,
    EdgeDetection,
    SaliencyMap,
    VisualizeSaliency,
    MorphologicalOperations
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
    method: str  # resize, normalize, gaussian, clahe, otsu, histogram, morphological, edge, morph_opening, morph_closing, visualize_saliency, saliency_map

# Carregando modelo e pipeline
model = keras.models.load_model('kerasmodel/skin_cancer.keras')
preprocess_pipeline = Pipeline([
    ('resize', Resize((128, 128))),
    ('blur', GaussianBlur()),
    ('morph_opening', MorphologicalOperations(operation='opening', kernel_size=(3, 3))),
    ('morph_closing', MorphologicalOperations(operation='closing', kernel_size=(3, 3))),
    ('clahe', CLAHE_Color())
])

@app.post("/analisar-imagem")
async def analisar_imagem_backend(
    file: UploadFile = File(...),
    usuario_id: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Salvar arquivo temporário
        temp_path = "temp_img.jpg"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        img = cv2.imread(temp_path)
        os.remove(temp_path)
        if img is None:
            raise HTTPException(status_code=400, detail="Imagem inválida.")

        original_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        processed = preprocess_pipeline.transform([original_rgb])[0]

        # Predição
        prediction = model.predict(np.expand_dims(processed, axis=0))[0][0]
        classe = "maligno" if prediction > 0.5 else "benigno"

        # Mapa de saliência
        saliency = SaliencyMap(model, processed)
        saliency_overlayed = VisualizeSaliency(original_rgb, saliency)

        # Função para codificar imagem em base64
        def encode_image(image):
            _, buffer = cv2.imencode('.jpg', image)
            return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode()}"

        imagem_final = encode_image(saliency_overlayed)
        imagem_original = encode_image(original_rgb)
        imagem_etapas = encode_image(cv2.hconcat([
            Resize((128, 128)).fit_transform([original_rgb])[0],
            GaussianBlur().fit_transform([original_rgb])[0],
            CLAHE_Color().fit_transform([original_rgb])[0]
        ]))

        # Salvar no banco
        nova = models.Imagem(
            usuario_id=usuario_id,
            original=imagem_original,
            resultado_final=imagem_final,
            metadados=imagem_etapas,
            diagnostico=classe,
            probabilidade=float(prediction),
            resize=None, normalize=None, gaussian=None, clahe=None, otsu=None,
            histogram=None, morphological=None, edgedetection=None
        )
        db.add(nova)
        db.commit()
        db.refresh(nova)

        return {
            "id": nova.id,
            "diagnostico": classe,
            "probabilidade": round(float(prediction), 4),
            "resultado_final": imagem_final,
            "etapas_processamento": imagem_etapas
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {e}")    

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

@app.get("/analises", response_model=List[schemas.ImagemResponse])
def listar_analises(usuario_id: str, db: Session = Depends(get_db)):
    imagens = db.query(models.Imagem).filter(models.Imagem.usuario_id == usuario_id).order_by(models.Imagem.data.desc()).all()
    return imagens


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
