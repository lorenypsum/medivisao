from sqlalchemy.orm import Session
import models, schemas

def criar_usuario(db: Session, user: schemas.UsuarioCreate):
    db_user = models.Usuario(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def deletar_usuario(db: Session, usuario_id: str):
    user = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def listar_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def get_usuario_por_username(db: Session, username: str):
    return db.query(models.Usuario).filter(models.Usuario.username == username).first()

def criar_imagem(db: Session, imagem: schemas.ImagemCreate):
    db_img = models.Imagem(**imagem.dict())
    db.add(db_img)
    db.commit()
    db.refresh(db_img)
    return db_img

def listar_imagens_do_usuario(db: Session, usuario_id: str):
    return db.query(models.Imagem).filter(models.Imagem.usuario_id == usuario_id).all()

def deletar_imagem(db: Session, imagem_id: str):
    img = db.query(models.Imagem).filter(models.Imagem.id == imagem_id).first()
    if img:
        db.delete(img)
        db.commit()
        return True
    return False

def salvar_ou_atualizar_imagem(db: Session, imagem: schemas.ImagemCreate):
    from models import Imagem
    existing = (
        db.query(Imagem)
        .filter(Imagem.usuario_id == imagem.usuario_id)
        .order_by(Imagem.data.desc())
        .first()
    )

    if existing:
        for campo, valor in imagem.dict().items():
            setattr(existing, campo, valor)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        nova = Imagem(**imagem.dict())
        db.add(nova)
        db.commit()
        db.refresh(nova)
        return nova

