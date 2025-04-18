import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import models

# Use environment variable for database URL, defaulting to SQLite for local development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/medivisao.db")

engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)
metadata = MetaData()
metadata.create_all(engine)
# try:
#     usuario = models.Usuario(name='a', username='a', password='a')
# except:
#     pass
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()
