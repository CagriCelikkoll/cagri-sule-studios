# docs/PROJE_BAGLAMI.md — Mülakat Simülatörü (ortak proje bağlamı)

> Bu dosya hem repoda (`docs/PROJE_BAGLAMI.md`) hem iki geliştiricinin Claude Project bilgisinde durur.
> Değiştirmek için PR gerekir; iki geliştirici de onaylamalı.

## Ürün

Yapay zekâ destekli mülakat simülatörü. Kullanıcı rol, seviye, dil (tr/en), mod (text/voice) ve persona seçer; isteğe bağlı CV ve iş ilanı yükler. Persona mülakatı yönetir; sonunda rubrikli rapor üretilir.

## Ekip ve sahiplik

| Alan | Sahip | Klasör |
|---|---|---|
| .NET backend: kimlik, oturum, SignalR hub, STT/TTS, konuşma metrikleri, saklama, arka plan işleri | Backend geliştiricisi | `backend/` |
| AI servisi: personalar, prompt'lar, plan, tur, rapor, değerlendirme seti | Şule | `ai-service/` |
| Web arayüzü | Şule | `web/` |
| Sözleşmeler | Ortak | `contracts/` |

## Mimari (değişmez kurallar)

1. Tarayıcı **yalnızca** .NET backend ile konuşur (REST `/api/v1` + SignalR `/hubs/interview`).
2. .NET **yalnızca** AI servisi ile konuşur (`/v1/*`, iç ağ, `X-Service-Key` başlığı).
3. AI servisi **durumsuzdur**: mülakat geçmişi, plan ve durum .NET'te saklanır ve her istekte gönderilir.
4. LLM anahtarları ve prompt'lar yalnızca AI servisindedir.
5. Konuşma metrikleri (WPM, dolgu kelimeleri, sessizlik) .NET'te deterministik hesaplanır; AI servisi bunları yorumlar, yeniden hesaplamaz.

## Teknoloji

- Backend: .NET 10, ASP.NET Core, EF Core, PostgreSQL, Redis, Hangfire, MinIO/S3, SignalR + MessagePack
- AI servisi: Python 3.12, FastAPI, Pydantic v2, SSE (`text/event-stream`)
- Web: Next.js (App Router), TypeScript, Tailwind, `@microsoft/signalr` + `@microsoft/signalr-protocol-msgpack`
- Yerel ortam: `docker compose up`

## İsimlendirme

- REST ve SignalR JSON'u: **camelCase** (.NET varsayılanı)
- AI servisi JSON'u: **snake_case** (Python/Pydantic varsayılanı). Dönüşümü .NET yapar.
- Kimlikler: UUID v7 string. Zamanlar: ISO 8601 UTC. Süreler: milisaniye (`*_ms` / `*Ms`).
- Dil kodları: `tr`, `en`.
- Persona kimlikleri: kebab-case (`hr-generalist`), sürüm tamsayı.

## Sözleşme dosyaları

- `contracts/rest-api.md`
- `contracts/realtime-hub.md`
- `contracts/ai-service-api.md`
- `contracts/schemas/*.schema.json` — JSON Schema 2020-12. CI'da örnek yükler bu şemalarla doğrulanır.
- `contracts/examples/*.json` — şemalara uyan örnekler; mock servisler bunları döndürebilir.

## Yetkinlik kimlikleri

`communication`, `problem_solving`, `technical_depth`, `ownership`, `teamwork`, `motivation_fit`, `structure`, `learning_agility` — tanımlar `ai-service/rubrics/competencies.yaml`.

## Mülakat durumu

`created → active ⇄ paused → completed → reported` (+ `failed`, `deleted`)

## Gizlilik (KVKK)

- Loglara transkript, CV veya ilan metni yazılmaz; yalnızca kimlikler, süreler, sayılar.
- CV metni AI servisine gitmeden önce .NET'te maskelenir (TC kimlik no, telefon, e-posta, adres).
- Ses kayıtları yalnızca kullanıcı onay verdiyse saklanır; varsayılan saklama 30 gün.

## Geliştirme notları

- Sözleşmeleri (contracts/) kendiliğinden değiştirme. Gerekirse değişiklik önerisini ayrı bir blokta yaz.
- Kod örneklerinde alan adlarını bu dosyadaki ve şemalardaki adlarla birebir kullan.
- Belirsizlikte varsayım yapma; açık soru olarak işaretle.
