# AI Servis API Sözleşmesi (v1)

.NET backend ↔ AI servisi. Sahibi: Şule. Taslak sürüm: `v1-draft-1`.

- Taban adres (yerel): `http://ai-service:8000`
- Kimlik doğrulama: her istekte `X-Service-Key: <paylaşılan gizli anahtar>` başlığı. Yoksa `401`.
- İzleme: .NET her istekte `X-Request-Id` ve `X-Interview-Id` gönderir; AI servisi loglarda bunları kullanır, cevapta `X-Request-Id`'yi geri yollar.
- JSON alanları **snake_case**.
- AI servisi **durumsuzdur**. Hiçbir uç nokta önceki isteği hatırlamaz.

## Uç noktalar

| Yöntem | Yol | Amaç | Zaman aşımı (.NET tarafı) |
|---|---|---|---|
| GET | `/health` | canlılık | 2 sn |
| GET | `/v1/personas` | persona kataloğu | 5 sn |
| POST | `/v1/plan` | mülakat planı üret | 30 sn |
| POST | `/v1/turn` | bir mülakatçı turu üret (SSE akışı) | ilk olay 5 sn, toplam 30 sn |
| POST | `/v1/report` | mülakat sonu raporu | 120 sn |

---

## GET /v1/personas

Cevap: `Persona` dizisi (şema: `schemas/persona.schema.json`). .NET bunu 10 dakika önbelleğe alır ve tarayıcıya camelCase olarak sunar.

```json
[
  {
    "id": "hr-generalist",
    "version": 1,
    "display_name": { "tr": "Elif — İK Uzmanı", "en": "Elif — HR Specialist" },
    "short_description": { "tr": "Sıcak ama dikkatli; motivasyon ve iletişim odaklı.", "en": "Warm but attentive; focuses on motivation and communication." },
    "interview_types": ["behavioral", "hr"],
    "difficulty": 2,
    "languages": ["tr", "en"],
    "voice": { "tr": "tr-TR-EmelNeural", "en": "en-US-JennyNeural" },
    "competencies": ["communication", "motivation_fit", "teamwork", "ownership", "structure"]
  }
]
```

`voice` yalnızca ipucudur; hangi TTS sesinin kullanılacağına .NET karar verir.

---

## POST /v1/plan

Mülakat başlarken bir kez çağrılır. Çıktı .NET'te `interviews.plan` alanına yazılır ve sonraki her `/v1/turn` isteğinde geri gönderilir.

İstek (şema: `schemas/plan-request.schema.json`):

```json
{
  "interview_id": "0192f6a4-7c1e-7b3a-9d2e-5f1a2b3c4d5e",
  "persona_id": "tech-lead-backend",
  "persona_version": 1,
  "language": "tr",
  "mode": "voice",
  "duration_min": 20,
  "profile": {
    "role": "Backend Developer",
    "level": "junior",
    "technologies": ["C#", ".NET", "PostgreSQL"]
  },
  "cv_text": "…maskelenmiş CV metni veya null…",
  "job_posting_text": "…iş ilanı metni veya null…"
}
```

Cevap: `Plan` (şema: `schemas/plan.schema.json`).

```json
{
  "plan_version": 1,
  "estimated_duration_min": 20,
  "competencies": [
    { "id": "technical_depth", "weight": 0.35 },
    { "id": "problem_solving", "weight": 0.25 },
    { "id": "communication", "weight": 0.2 },
    { "id": "ownership", "weight": 0.2 }
  ],
  "questions": [
    {
      "id": "q1",
      "type": "warmup",
      "text": "Kısaca kendinden ve son projenden bahseder misin?",
      "competency_ids": ["communication"],
      "difficulty": 1,
      "expected_points": ["rolü", "kullandığı teknolojiler", "kendi katkısı"],
      "max_follow_ups": 1
    },
    {
      "id": "q2",
      "type": "technical",
      "text": "Bir API'de N+1 sorgu problemini nasıl fark eder ve çözersin?",
      "competency_ids": ["technical_depth", "problem_solving"],
      "difficulty": 3,
      "expected_points": ["N+1 tanımı", "profiling/log", "eager loading veya projection", "ölçüm"],
      "max_follow_ups": 2
    }
  ]
}
```

Kurallar:
- `questions` en az 3, en fazla 15 eleman. İlki `warmup`, sonuncusu `closing` olmalı.
- `cv_text`/`job_posting_text` varsa en az bir soru `cv_deep_dive` ya da ilandaki bir gereksinime dayanmalı.
- `weight` toplamı 1.0 (±0.01).

---

## POST /v1/turn (SSE)

Her mülakatçı konuşması için bir kez. Açılış turunda `candidate_turn` = `null`.

İstek (şema: `schemas/turn-request.schema.json`):

```json
{
  "interview_id": "0192f6a4-7c1e-7b3a-9d2e-5f1a2b3c4d5e",
  "persona_id": "tech-lead-backend",
  "persona_version": 1,
  "language": "tr",
  "mode": "voice",
  "profile": { "role": "Backend Developer", "level": "junior", "technologies": ["C#", ".NET"] },
  "plan": { "…": "/v1/plan cevabının aynısı" },
  "state": {
    "current_question_id": "q2",
    "follow_ups_used": 1,
    "asked_question_ids": ["q1", "q2"],
    "elapsed_sec": 412,
    "remaining_sec": 788,
    "token_budget_remaining": 42000
  },
  "history": [
    { "index": 0, "speaker": "interviewer", "text": "Merhaba, ben Kaan…", "question_id": "q1" },
    { "index": 1, "speaker": "candidate", "text": "Merhaba, ben…" },
    { "index": 2, "speaker": "interviewer", "text": "N+1 problemini…", "question_id": "q2", "interrupted_at_char": null }
  ],
  "candidate_turn": {
    "index": 3,
    "text": "Iıı şey, EF Core'da Include kullanarak…",
    "metrics": {
      "duration_ms": 41200,
      "word_count": 96,
      "wpm": 139.8,
      "filler_count": 5,
      "fillers": { "ıı": 3, "şey": 2 },
      "long_pause_count": 1,
      "longest_pause_ms": 3100,
      "time_to_first_word_ms": 1800
    }
  }
}
```

Yazılı modda `metrics` içinde yalnızca `word_count` ve `time_to_first_word_ms` (cevap yazmaya başlama süresi yerine gönderme süresi) dolu gelir; diğerleri `null`.

Cevap: `Content-Type: text/event-stream`. Olaylar sırayla:

```
event: delta
data: {"text": "Include kullanmak "}

event: delta
data: {"text": "iyi bir başlangıç. "}

event: final
data: {"text": "Include kullanmak iyi bir başlangıç. Peki bunun bir N+1 olduğunu ilk başta nasıl fark ederdin?", "decision": {"action": "follow_up", "question_id": "q2", "reason": "Tespit yöntemi hiç anlatılmadı."}, "usage": {"input_tokens": 3120, "output_tokens": 48, "model": "claude-haiku-5-5"}}
```

Hata durumunda:

```
event: error
data: {"code": "llm_timeout", "message": "LLM did not respond in time", "retryable": true}
```

`final` olayının şeması: `schemas/turn-final.schema.json`.

`decision.action` değerleri:

| Değer | Anlamı | .NET ne yapar |
|---|---|---|
| `follow_up` | Aynı soruda derinleş | `follow_ups_used += 1` |
| `next_question` | `question_id` ile verilen yeni soruya geç | `current_question_id` güncellenir, `follow_ups_used = 0` |
| `wrap_up` | Süre/plan bitti; kapanış sorusu soruluyor | durum aynı, son tur sayılır |
| `end` | Mülakat bitti (kapanış cümlesi söylendi) | mülakat `completed`, rapor işi başlar |

Kurallar:
- `delta` parçalarının birleşimi `final.text` ile **birebir** aynı olmalı. .NET TTS'i deltalardan cümle cümle besler.
- İlk `delta` hedefi: istekten sonra ≤ 800 ms. İlk cümle kısa tutulmalı (sesli modda gecikmeyi düşürür).
- Mülakatçı turu sesli modda en fazla 3 cümle, yazılı modda en fazla 5 cümle.
- `remaining_sec < 90` ise AI servisi `wrap_up` veya `end`'e yönelmeli.
- `token_budget_remaining < 2000` ise doğrudan `end`.

### Araya girme (barge-in)

Kullanıcı mülakatçıyı keserse .NET akışı iptal eder (HTTP bağlantısını kapatır). AI servisi istemci bağlantısı kopunca LLM çağrısını da iptal etmeli. Bir sonraki istekte kesilen tur `history` içinde `interrupted_at_char` dolu gelir; mülakatçı bunu fark edip doğal davranmalı ("Tabii, buyurun").

---

## POST /v1/report

Mülakat `completed` olduğunda arka plan işi çağırır. Akış yok, tek JSON.

İstek (şema: `schemas/report-request.schema.json`): `interview_id`, `persona_id`, `persona_version`, `language`, `mode`, `profile`, `plan`, `history` (tamamı), `session_metrics`:

```json
{
  "session_metrics": {
    "total_duration_ms": 1184000,
    "candidate_talk_ratio": 0.62,
    "avg_wpm": 131.2,
    "filler_per_min": 4.1,
    "top_fillers": { "ıı": 21, "şey": 9, "yani": 7 },
    "long_pause_count": 6,
    "avg_time_to_first_word_ms": 1650
  }
}
```

Cevap: `Report` (şema: `schemas/report.schema.json`). Örnek:

```json
{
  "rubric_version": 1,
  "language": "tr",
  "overall_score": 50,
  "summary": "Teknik temelin sağlam; cevapların ölçüm ve sonuç kısmında zayıflıyor.",
  "competency_scores": [
    {
      "competency_id": "technical_depth",
      "score": 3,
      "comment": "N+1'i doğru tanımladın ama tespit yöntemini sorulunca açıkladın.",
      "evidence": [ { "turn_index": 3, "quote": "EF Core'da Include kullanarak" } ]
    }
  ],
  "question_feedback": [
    {
      "question_id": "q2",
      "strengths": ["Çözümü doğru seçtin."],
      "improvements": ["Problemi nasıl ölçtüğünü baştan söyle."],
      "better_answer_example": "Önce log'da aynı sorgunun tekrarlandığını görürüm…",
      "star": null
    }
  ],
  "speech_feedback": {
    "comments": ["Dakikada ~4 dolgu kelimesi var; en sık 'ıı'. Cevaba başlamadan 1 saniye düşünmek bunu azaltır."]
  },
  "next_steps": ["Davranışsal sorularda sonucu sayıyla bitir.", "SQL profiling araçlarını bir örnekle anlatabilmeyi çalış."]
}
```

Kurallar:
- Her `competency_scores[].score` 1–5 tamsayı; rubrikteki tanımlara dayanmalı (`ai-service/rubrics/competencies.yaml`).
- Her puan için en az bir `evidence`; `quote` adayın gerçekten söylediği metinden, en fazla 20 kelime.
- `overall_score` = puanlanan yetkinliklerin ağırlıklı ortalamasının 0–100'e ölçeklenmiş hali: `ort = Σ(weight·score) / Σ(weight)`, `overall_score = round((ort − 1) / 4 · 100)`. Bu hesabı LLM değil kod yapar (LLM'in verdiği sayı yok sayılır, yeniden hesaplanır).
- Tam örnekler: `contracts/examples/*.json` (hepsi şemalara karşı doğrulanmış).
- `star` yalnızca `behavioral` sorularda dolu: `{ "situation": bool, "task": bool, "action": bool, "result": bool }`.
- Konuşma yorumları `session_metrics` sayılarına dayanmalı; AI servisi bu sayıları yeniden hesaplamaz.

## Hata kodları (tüm uç noktalar)

| HTTP | `code` | `retryable` |
|---|---|---|
| 400 | `invalid_request` | false |
| 401 | `unauthorized` | false |
| 404 | `persona_not_found` | false |
| 422 | `schema_violation` (LLM çıktısı onarımdan sonra da geçersiz) | true |
| 429 | `rate_limited` | true |
| 503 | `llm_unavailable` | true |
| 504 | `llm_timeout` | true |

Gövde: `{ "code": "...", "message": "...", "retryable": true }`

.NET yeniden deneme politikası: `retryable` ise 1 kez, 500 ms bekleyerek. `/v1/turn`'de ilk `delta` geldikten sonra yeniden deneme yapılmaz.
