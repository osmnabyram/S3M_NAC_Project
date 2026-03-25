from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"mesaj": "NAC Sistemi API'si Çalışıyor!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}