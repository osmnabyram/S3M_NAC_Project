FROM python:3.13-slim

WORKDIR /app

# Gerekli kütüphaneleri yüklemek için
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Uygulamayı başlatmak için
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]