# Mülakat Simülatörü

Yapay zekâ destekli bir mülakat simülatörü: kullanıcı rol, seviye, dil (tr/en), mod (yazılı/sesli) ve bir mülakatçı personası seçer; isteğe bağlı olarak CV ve iş ilanı yükler.
Persona mülakatı gerçek zamanlı yönetir, cevaplara göre takip soruları sorar.
Mülakat sonunda yetkinlik puanları, kanıt cümleleri, daha iyi cevap örnekleri ve konuşma metrikleri içeren bir rapor üretilir.

Ayrıntılı proje bağlamı: [`docs/PROJE_BAGLAMI.md`](docs/PROJE_BAGLAMI.md) · Başlangıç notu: [`docs/BASLANGIC.md`](docs/BASLANGIC.md)

## Klasör yapısı

```
backend/        .NET 10 backend (ASP.NET Core, EF Core, PostgreSQL)
  src/MulakatSim.Api             giriş noktası (minimal API)
  src/MulakatSim.Domain          varlıklar ve enum'lar
  src/MulakatSim.Infrastructure  EF Core, dış servis istemcileri
  tests/MulakatSim.Tests         xUnit testleri
ai-service/     Python + FastAPI AI servisi (personalar, prompt'lar, rubrikler, değerlendirme seti)
web/            Next.js web arayüzü
contracts/      ortak sözleşmeler: REST, SignalR, AI servisi API'si, JSON şemaları ve örnekler
docs/           proje bağlamı, başlangıç notu, mimari karar kayıtları (adr/)
```

## Gereksinimler

- Docker + Docker Compose v2
- .NET 10 SDK (backend'i yerelde derlemek/test etmek için)
- Python 3.12 (sözleşme doğrulama betiği ve AI servisi için)
- Node.js 22+ (web arayüzü için)

## Çalıştırma

```bash
cp .env.example .env          # değerleri düzenle
docker compose up             # postgres, redis, minio, backend
docker compose --profile full up   # + ai-service ve web (Dockerfile'ları eklendiğinde)
```

- Backend: http://localhost:8080 — sağlık kontrolü `GET /health`, OpenAPI `GET /openapi/v1.json`
- MinIO konsolu: http://localhost:9001

Backend testleri:

```bash
dotnet test backend/MulakatSim.sln
```

Sözleşme doğrulama:

```bash
pip install jsonschema pyyaml
python contracts/generate_and_validate.py .
```

## Dal kuralları

- `main` korumalı; doğrudan push yapılmaz.
- Dallar: `feature/<alan>-<konu>` (ör. `feature/backend-auth`, `feature/ai-persona-loader`, `feature/web-interview-screen`).
- Her değişiklik PR ile birleşir; karşı taraf inceler.
- `contracts/` değişiklikleri iki geliştiricinin de onayını gerektirir.
- Mimari kararlar `docs/adr/` altına kısa notlar olarak eklenir.
