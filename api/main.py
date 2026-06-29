from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import models, database
import redis
import os
import json
from datetime import datetime

# Veritabanı tablolarını oluştur
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="S3M NAC Policy Engine")

# Redis bağlantısı
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

@app.get("/")
def read_root():
    return {"message": "S3M NAC Policy Engine is running!"}

@app.post("/auth")
async def authenticate(request: Request, db: Session = Depends(database.get_db)):
    data = await request.json()
    username = data.get("User-Name") or data.get("Calling-Station-Id")
    password = data.get("User-Password")
    
    if not username:
        return {"control:Auth-Type": "Reject"}

    # Rate limiting (Örn: 1 dakikada 5 başarısız deneme)
    fail_key = f"fail_count:{username}"
    fails = redis_client.get(fail_key)
    if fails and int(fails) >= 5:
        return {"control:Auth-Type": "Reject", "Reply-Message": "Rate limit exceeded"}

    # Kullanıcıyı veritabanında ara
    radcheck = db.query(models.RadCheck).filter(models.RadCheck.username == username).all()
    if not radcheck:
        redis_client.incr(fail_key)
        redis_client.expire(fail_key, 60)
        return {"control:Auth-Type": "Reject"}

    # PAP veya MAB Kontrolü
    auth_type = "Reject"
    for check in radcheck:
        # 1. PAP (Şifre) kontrolü
        if check.attribute == "Cleartext-Password" and check.value == password:
            auth_type = "Accept"
            break
        # 2. MAB (MAC Bypass) kontrolü - Şifresiz giriş
        if check.attribute == "Auth-Type" and check.value == "Accept" and not password:
            auth_type = "Accept"
            break
            
    if auth_type == "Reject":
        redis_client.incr(fail_key)
        redis_client.expire(fail_key, 60)
        return {"control:Auth-Type": "Reject"}

    # Başarılı girişte fail sayacını sıfırla
    redis_client.delete(fail_key)
    return {"control:Auth-Type": "Accept"}

@app.post("/authorize")
async def authorize(request: Request, db: Session = Depends(database.get_db)):
    data = await request.json()
    username = data.get("User-Name") or data.get("Calling-Station-Id")
    
    if not username:
        return {}
        
    # Kullanıcının grubunu bul
    user_group = db.query(models.RadUserGroup).filter(models.RadUserGroup.username == username).first()
    if not user_group:
        return {}
        
    # Gruba ait politikaları/VLAN bilgilerini çek
    group_replies = db.query(models.RadGroupReply).filter(models.RadGroupReply.groupname == user_group.groupname).all()
    
    reply_dict = {}
    for reply in group_replies:
        # FreeRADIUS'a "reply:Attribute-Name" formatında dönmeliyiz
        reply_dict[f"reply:{reply.attribute}"] = reply.value
        
    return reply_dict

@app.post("/accounting")
async def accounting(request: Request, db: Session = Depends(database.get_db)):
    data = await request.json()
    
    status_type = data.get("Acct-Status-Type")
    session_id = data.get("Acct-Session-Id")
    username = data.get("User-Name") or data.get("Calling-Station-Id")
    nas_ip = data.get("NAS-IP-Address")
    
    if not session_id or not username:
        return {}
        
    session_key = f"session:{session_id}"
        
    if status_type == "Start":
        new_acct = models.RadAcct(
            acctsessionid=session_id,
            username=username,
            nasipaddress=nas_ip,
            acctstarttime=datetime.utcnow(),
            callingstationid=data.get("Calling-Station-Id", "")
        )
        db.add(new_acct)
        db.commit()
        
        # Aktif oturumu Redis'e kaydet (Hızlı sorgulama için)
        redis_client.set(session_key, json.dumps({
            "username": username,
            "nas_ip": nas_ip,
            "start_time": datetime.utcnow().isoformat()
        }))
        
    elif status_type == "Interim-Update":
        acct = db.query(models.RadAcct).filter(models.RadAcct.acctsessionid == session_id).first()
        if acct:
            acct.acctupdatetime = datetime.utcnow()
            acct.acctinputoctets = data.get("Acct-Input-Octets", 0)
            acct.acctoutputoctets = data.get("Acct-Output-Octets", 0)
            db.commit()
            
    elif status_type == "Stop":
        acct = db.query(models.RadAcct).filter(models.RadAcct.acctsessionid == session_id).first()
        if acct:
            acct.acctstoptime = datetime.utcnow()
            acct.acctinputoctets = data.get("Acct-Input-Octets", 0)
            acct.acctoutputoctets = data.get("Acct-Output-Octets", 0)
            acct.acctterminatecause = data.get("Acct-Terminate-Cause", "")
            if acct.acctstarttime:
                acct.acctsessiontime = int((datetime.utcnow() - acct.acctstarttime).total_seconds())
            db.commit()
            
        # Oturum kapandığında Redis'ten sil
        redis_client.delete(session_key)
        
    return {}

@app.get("/users")
def get_users(db: Session = Depends(database.get_db)):
    users = db.query(models.RadCheck).all()
    return [{"username": u.username, "attribute": u.attribute, "value": u.value} for u in users]

@app.get("/sessions/active")
def get_active_sessions():
    keys = redis_client.keys("session:*")
    sessions = []
    for key in keys:
        data = redis_client.get(key)
        if data:
            sessions.append(json.loads(data))
    return sessions