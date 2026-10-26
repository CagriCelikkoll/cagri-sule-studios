# ADR 0001 — Temel mimari kararlar

- **Durum:** Kabul edildi
- **Tarih:** 2026-10-26

## Bağlam

İki geliştirici ayrı alanlarda (backend / AI servisi + web) paralel çalışacak. Alanlar arasındaki sınırların ve temel teknoloji seçimlerinin baştan sabitlenmesi gerekiyor. Ayrıntılar: `docs/PROJE_BAGLAMI.md`.

## Kararlar

### Mimari kurallar

1. Tarayıcı **yalnızca** .NET backend ile konuşur (REST `/api/v1` + SignalR `/hubs/interview`).
2. .NET **yalnızca** AI servisi ile konuşur (`/v1/*`, iç ağ, `X-Service-Key` başlığı).
3. AI servisi **durumsuzdur**: mülakat geçmişi, plan ve durum .NET'te saklanır, her istekte gönderilir.
4. LLM anahtarları ve prompt'lar yalnızca AI servisindedir.
5. Konuşma metrikleri (WPM, dolgu kelimeleri, sessizlik) .NET'te deterministik hesaplanır; AI servisi yalnızca yorumlar.
6. REST/SignalR JSON'u camelCase, AI servisi JSON'u snake_case; dönüşümü .NET yapar.
7. Loglara kullanıcı metni (transkript, CV, ilan) yazılmaz (KVKK).

### Teknoloji ve kapsam

| Konu | Karar |
|---|---|
| AI servisi | Python + FastAPI (Pydantic v2, SSE) |
| Arayüz | Yalnızca web: Next.js (App Router), PWA. Mobil uygulama kapsam dışı |
| STT/TTS | Azure Speech |
| MVP dili | İki dilli: Türkçe + İngilizce birlikte |
| LLM | Sağlayıcıdan bağımsız; AI servisi içinde soyutlama katmanı arkasında. Geliştirmede ücretsiz katman yalnızca **sahte veriyle** kullanılır (gerçek CV/transkript gönderilmez) |

## Sonuçlar

- Sözleşmeler (`contracts/`) iki alan arasındaki tek bağlantı noktasıdır; değişiklikleri iki onay gerektirir.
- LLM sağlayıcısını değiştirmek yalnızca AI servisini etkiler.
- Tek arayüz hedefi, MVP'de iş yükünü düşürür; PWA ile mobil tarayıcı desteği sağlanır.
- İki dilli MVP, persona/prompt/rubrik içeriklerinin baştan `tr`/`en` olarak yazılmasını gerektirir.
