import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env dosyasındaki verileri yüklüyoruz
load_dotenv()

# Önce tek parça DATABASE_URL'e bak (Docker environment), yoksa parça parça oluştur
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URL:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = os.getenv("DB_PORT", "5432")
    SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Docker compose'un verdiği "postgresql://" prefix'ini "postgresql+psycopg://" yap
if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Veritabanı motorunu (engine) oluşturuyoruz
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Veritabanı ile konuşacak oturum fabrikası
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tablo sınıflarımızın miras alacağı ana sınıf
Base = declarative_base()

# İstek geldiğinde DB bağlantısı açıp iş bitince kapatan yardımcı fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()