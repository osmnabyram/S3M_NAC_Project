from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database

app = FastAPI(title="S3M NAC Policy Engine")

# RADIUS sunucusundan bize gelecek isteğin şablonu
class AuthRequest(BaseModel):
    username: str
    password: str

@app.get("/")
def read_root():
    return {"message": "S3M NAC Policy Engine is running!"}

@app.get("/test-db")
def test_db(db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == "s3m_admin").first()
    if user:
        return {
            "status": "Success",
            "message": "Veritabanına bağlanıldı!",
            "found_user": {
                "username": user.username,
                "role": user.role,
                "vlan": user.vlan_id
            }
        }
    return {"status": "Error", "message": "Kullanıcı bulunamadı!"}

# --- YENİ EKLENEN KISIM: KİMLİK DOĞRULAMA (AUTH) KAPISI ---
@app.post("/auth")
def authenticate_user(request: AuthRequest, db: Session = Depends(database.get_db)):
    # 1. Kullanıcıyı veritabanında ara
    user = db.query(models.User).filter(models.User.username == request.username).first()
    
    # 2. Kullanıcı yoksa veya hesabı pasife alınmışsa (is_active=False) kapıdan çevir
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Access Denied: Kullanıcı bulunamadı veya pasif.")
        
    # 3. Şifre kontrolü (PDF'e göre ileride buraya hash kontrolü ekleyeceğiz)
    if user.password_hash != request.password:
        raise HTTPException(status_code=401, detail="Access Denied: Hatalı şifre.")
        
    # 4. Giriş Başarılı! RADIUS sunucusunun anlayacağı dilde VLAN ve yetki bilgilerini gönder
    return {
        "status": "Accept",
        "message": "Access Granted",
        "radius_attributes": {
            "Tunnel-Type": 13,  # VLAN Tüneli
            "Tunnel-Medium-Type": 6,  # IEEE-802 (Ethernet/Wi-Fi)
            "Tunnel-Private-Group-Id": str(user.vlan_id),  # Kullanıcının atanacağı VLAN ID
            "Filter-Id": user.role  # Kullanıcının rolü (admin/user vb.)
        }
    }