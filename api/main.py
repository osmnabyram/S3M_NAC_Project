from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models, database

# 🔥 EKSİK TABLOLARI OTOMATİK OLUŞTURACAK SİHİRLİ SATIR:
database.Base.metadata.create_all(bind=database.engine)

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

# --- KİMLİK DOĞRULAMA (AUTH) VE KAYIT TUTMA (ACCOUNTING) KAPISI ---
@app.post("/auth")
def authenticate_user(request: AuthRequest, db: Session = Depends(database.get_db)):
    # 1. Kullanıcıyı veritabanında ara
    user = db.query(models.User).filter(models.User.username == request.username).first()
    
    # 2. Log nesnesini hazırla (Han Defteri)
    new_log = models.RadiusLog(username=request.username)
    
    # 3. Kullanıcı yoksa veya hesabı pasife alınmışsa kapıdan çevir ve logla
    if not user or not user.is_active:
        new_log.auth_status = "Access-Reject"
        db.add(new_log)
        db.commit()
        raise HTTPException(status_code=401, detail="Access Denied: Kullanıcı bulunamadı veya pasif.")
        
    # 4. Şifre kontrolü hatalıysa kapıdan çevir ve logla
    if user.password_hash != request.password:
        new_log.auth_status = "Access-Reject"
        db.add(new_log)
        db.commit()
        raise HTTPException(status_code=401, detail="Access Denied: Hatalı şifre.")
        
    # 5. Giriş Başarılı! Logu doldur, veritabanına kaydet
    new_log.auth_status = "Access-Accept"
    new_log.vlan_id = user.vlan_id
    db.add(new_log)
    db.commit()
    
    # 6. RADIUS sunucusunun anlayacağı dilde VLAN ve yetki bilgilerini gönder
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