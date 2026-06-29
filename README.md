# S3M Network Access Control (NAC) Projesi

Bu proje, S3M stajyer değerlendirme ödevi kapsamında geliştirilmiş, RADIUS protokolünü kullanan temel düzeyde bir Network Access Control (NAC) sistemidir.

## Özellikler
- **Kimlik Doğrulama (Authentication):** PAP (Şifre tabanlı) ve MAB (MAC Authentication Bypass) desteklenmektedir.
- **Yetkilendirme (Authorization):** Kullanıcı gruplarına göre dinamik VLAN ataması yapılmaktadır.
- **Hesap Yönetimi (Accounting):** Kullanıcı oturum süreleri, aktarılan veri (input/output octets) PostgreSQL üzerinde saklanmakta ve aktif oturumlar Redis'te cache'lenmektedir.
- **Altyapı:** Docker Compose kullanılarak PostgreSQL, Redis, FreeRADIUS ve FastAPI (Policy Engine) servisleri orkestre edilmiştir.

## Mimari

Sistem 4 ana bileşenden oluşur:
1. **FreeRADIUS:** İstemcilerden gelen RADIUS isteklerini karşılar ve `rlm_rest` modülü aracılığıyla FastAPI Policy Engine'e iletir.
2. **FastAPI (Policy Engine):** İş mantığının (Authentication, Authorization, Accounting) yürütüldüğü REST API.
3. **PostgreSQL:** Kullanıcı, grup, yetki ve oturum kayıtlarının tutulduğu kalıcı veritabanı.
4. **Redis:** Başarısız giriş denemeleri (Rate Limiting) ve aktif oturumların takibi için kullanılan bellek içi veri yapısı deposu.

## Kurulum ve Çalıştırma

1. Repoyu klonlayın ve proje dizinine gidin.
2. `.env.example` dosyasını kopyalayarak `.env` dosyasını oluşturun:
   ```bash
   cp .env.example .env
   ```
3. Docker Compose ile tüm servisleri başlatın:
   ```bash
   docker-compose up -d --build
   ```
   > İlk çalıştırmada veritabanı tabloları `db/init.sql` üzerinden ve FastAPI `Base.metadata.create_all` ile otomatik olarak oluşturulacaktır. Varsayılan test verileri (admin kullanıcısı ve cihaz MAC adresi) eklenecektir.

## Test Senaryoları

Sistem ayağa kalktıktan sonra aşağıdaki komutlarla test yapabilirsiniz. Testleri yapabilmek için sisteminizde `radtest` ve `radclient` kurulu olmalıdır (veya FreeRADIUS container'ına girerek de çalıştırabilirsiniz).

### 1. PAP Doğrulama Testi
```bash
radtest s3m_admin testing123 localhost:1812 0 testing123
```
*Beklenen Sonuç:* `Access-Accept` ve `Tunnel-Private-Group-Id` (VLAN) ataması.

### 2. MAB (MAC Bypass) Doğrulama Testi
```bash
echo "User-Name=AA:BB:CC:DD:EE:FF, Calling-Station-Id=AA:BB:CC:DD:EE:FF" | radclient -x localhost:1812 auth testing123
```
*Beklenen Sonuç:* `Access-Accept` ve cihazlara özel VLAN ataması.

### 3. API Endpoint'lerini Görüntüleme
Tarayıcınızdan veya curl ile FastAPI Swagger dokümantasyonuna ulaşabilirsiniz:
[http://localhost:8000/docs](http://localhost:8000/docs)

Aktif kullanıcıları veya oturumları listeleyebilirsiniz:
```bash
curl http://localhost:8000/users
curl http://localhost:8000/sessions/active
```

## Güvenlik
- Şifreler ve secret'lar `.env` dosyası üzerinden yönetilir ve git repository'sine eklenmez.
- Hatalı giriş denemelerine karşı Redis tabanlı Rate Limiting uygulanmaktadır (1 dakikada 5 deneme kısıtı).
