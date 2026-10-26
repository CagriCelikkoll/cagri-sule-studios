# REST API Sözleşmesi (v1)

Tarayıcı ↔ .NET. Sahibi: backend. Taban: `/api/v1`. JSON alanları **camelCase**.
Kimlik: `Authorization: Bearer <accessToken>` (giriş dışındaki her uç nokta). Erişim tokenı 15 dk, yenileme tokenı 30 gün (httpOnly cookie).

OpenAPI dosyası .NET'ten otomatik üretilir: `GET /openapi/v1.json`. Şule arayüz tiplerini buradan üretebilir (`openapi-typescript`).

## Hata biçimi (RFC 7807)

```json
{ "type": "about:blank", "title": "Validation failed", "status": 400, "code": "validation_failed",
  "errors": { "durationMin": ["10 ile 45 arasında olmalı"] } }
```

## Kimlik

| Yöntem | Yol | Gövde | Cevap |
|---|---|---|---|
| POST | `/auth/register` | `{ email, password, displayName, consents: { audioStorage, crossBorderTransfer } }` | `201 { accessToken, user }` |
| POST | `/auth/login` | `{ email, password }` | `200 { accessToken, user }` |
| POST | `/auth/google` | `{ idToken }` | `200 { accessToken, user }` |
| POST | `/auth/refresh` | — (cookie) | `200 { accessToken }` |
| POST | `/auth/logout` | — | `204` |

`crossBorderTransfer: false` olan kullanıcı mülakat başlatamaz (LLM/STT yurt dışında); arayüz bunu açıklamalı.

## Kullanıcı

| Yöntem | Yol | Açıklama |
|---|---|---|
| GET | `/me` | `{ id, email, displayName, preferredLanguage, consents, quota: { dailyLimit, usedToday } }` |
| PATCH | `/me` | `displayName`, `preferredLanguage`, `consents` |
| DELETE | `/me` | Hesap + tüm veri silinir (KVKK). `202` döner, silme arka planda |

## Belgeler

| Yöntem | Yol | Açıklama |
|---|---|---|
| POST | `/documents` | `multipart/form-data`: `file` (PDF/DOCX ≤ 5 MB) **veya** `text`, ve `kind` = `cv` \| `job_posting` |
| GET | `/documents` | Kullanıcının belgeleri |
| DELETE | `/documents/{id}` | Sil |

`POST /documents` cevabı:

```json
{ "id": "…", "kind": "cv", "fileName": "cv.pdf", "charCount": 3812,
  "preview": "Yazılım mühendisliği 4. sınıf…", "maskedFields": ["phone", "email"] }
```

## Personalar

`GET /personas` → AI servisindeki katalog, camelCase: `[{ id, version, displayName, shortDescription, interviewTypes, difficulty, languages }]`. `displayName` ve `shortDescription` `{ tr, en }` nesneleri.

## Mülakatlar

`POST /interviews`

```json
{
  "personaId": "tech-lead-backend",
  "language": "tr",
  "mode": "voice",
  "durationMin": 20,
  "profile": { "role": "Backend Developer", "level": "junior", "technologies": ["C#", ".NET"] },
  "cvDocumentId": null,
  "jobPostingDocumentId": "…"
}
```

- `level`: `intern` | `junior` | `mid` | `senior`
- `mode`: `text` | `voice`
- `durationMin`: 10–45

Cevap `201`:

```json
{ "id": "…", "status": "created", "hubUrl": "/hubs/interview", "plan": { "totalQuestions": 7, "estimatedDurationMin": 20 } }
```

Plan oluşturma bu çağrı içinde yapılır (AI servisi `/v1/plan`, ~5–15 sn). Arayüz bu sırada yükleniyor ekranı gösterir. Planın soruları kullanıcıya **gösterilmez**.

| Yöntem | Yol | Açıklama |
|---|---|---|
| GET | `/interviews?page=1&pageSize=20` | Liste: `{ items: [{ id, personaId, role, mode, status, startedAt, overallScore }], total }` |
| GET | `/interviews/{id}` | Ayrıntı + durum |
| GET | `/interviews/{id}/transcript` | `[{ index, speaker, text, startMs, endMs, hasAudio }]` |
| GET | `/interviews/{id}/turns/{index}/audio` | Ses dosyası (süreli imzalı URL'ye yönlendirir) |
| GET | `/interviews/{id}/report` | Rapor (AI servisinin rapor JSON'unun camelCase hali + `sessionMetrics`). Hazır değilse `202 { status: "generating" }` |
| GET | `/interviews/{id}/report.pdf` | PDF |
| POST | `/interviews/{id}/end` | Erken bitir (hub kapalıysa) |
| DELETE | `/interviews/{id}` | Mülakatı, sesleri ve raporu sil |

## İlerleme

`GET /progress?range=90d`

```json
{
  "interviewCount": 8,
  "competencies": [
    { "id": "communication", "points": [ { "date": "2026-10-02", "score": 3 }, { "date": "2026-10-20", "score": 4 } ] }
  ],
  "speech": [ { "date": "2026-10-20", "fillerPerMin": 4.1, "avgWpm": 131 } ],
  "weakest": ["ownership"]
}
```
