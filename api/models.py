from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base

# 1. KULLANICI TABLOSU (SİLİNMİŞ OLAN buydu)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="user")
    vlan_id = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)

# 2. HAN DEFTERİ / LOG TABLOSU (Yeni eklediğimiz)
class RadiusLog(Base):
    __tablename__ = "radius_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    auth_status = Column(String)  # "Access-Accept" veya "Access-Reject"
    vlan_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)