# Şule, hoş geldin 👋 — Mülakat Simülatörü başlangıç notu

Bu paket, projeye benim tarafımdan (.NET backend) hazırlanmış ortak zemin. Amacı şu: ikimiz ayrı ayrı Claude ile çalışacağız; iki Claude'un da aynı projeyi, aynı arayüzleri bilmesi lazım. O yüzden her şey yazılı ve bu klasörde.

Ayrıntılı plan (özellikler, mimari diyagramı, yol haritası, riskler) ayrı bir dokümanda; linkini sana ayrıca atıyorum.

---

## 1. Proje tek paragrafta

Kullanıcı meslek/teknoloji ve seviye seçer, isterse CV'sini ve iş ilanını yükler. Seçtiği **persona** (İK uzmanı, teknik lider, startup CTO'su, stres mülakatçısı…) ona **yazılı veya sesli** mülakat yapar. Sonunda yetkinlik bazlı puanlar, kanıt cümleleri, "daha iyi cevap" örnekleri ve konuşma metrikleri (konuşma hızı, dolgu kelimeleri, duraksamalar) içeren bir rapor alır.

## 2. Kim ne yapıyor

| | Ben (.NET) | Sen (AI + arayüz) |
|---|---|---|
| Kimlik, kullanıcı, oturum durumu | ✅ | |
| SignalR gerçek zamanlı kanal (ses + metin) | ✅ | istemci tarafı ✅ |
| STT / TTS (ses ↔ metin) | ✅ | |
| Konuşma metrikleri (WPM, dolgu kelimesi, sessizlik) | ✅ hesaplar | ✅ rapora yorumlar |
| Personalar, prompt'lar, mülakat planı | | ✅ |
| Tur bazlı mülakatçı cevabı + takip sorusu kararı | | ✅ |
| Rubrikli rapor üretimi | saklar, PDF yapar | ✅ üretir |
| Web arayüzü (Next.js) | | ✅ |
| Mikrofon, VAD, ses oynatma, araya girme | | ✅ |

**Altın kural:** Tarayıcı sadece .NET ile konuşur. .NET sadece senin AI servisinle konuşur. LLM anahtarları ve prompt'lar sadece senin serviste yaşar.

## 3. Bu klasörde ne var

```
docs/
  BASLANGIC.md                   ← bu dosya
  PROJE_BAGLAMI.md               ← ortak proje bağlamı (Claude Projene de yükle)
  adr/                           ← mimari karar kayıtları
contracts/
  rest-api.md                    ← tarayıcı ↔ .NET REST uçları
  realtime-hub.md                ← tarayıcı ↔ .NET SignalR olayları
  ai-service-api.md              ← .NET ↔ senin AI servisin (EN ÖNEMLİSİ)
  schemas/*.schema.json          ← JSON şemaları (CI'da ikimiz de bunlarla doğrularız)
  examples/*.json                ← şemalara uyan tam örnek istek/cevaplar (mock'lar için hazır)
  generate_and_validate.py       ← şemaları üretip örnekleri doğrulayan betik
ai-service/
  personas/*.yaml                ← 4 başlangıç personası (taslak, senin)
  prompts/interviewer_system.md  ← mülakatçı sistem prompt şablonu (taslak)
  prompts/report_system.md       ← rapor üretim prompt'u (taslak)
  rubrics/competencies.yaml      ← yetkinlikler ve 1/3/5 puan tanımları
  evals/                         ← prompt kalite testi için örnek vaka + açıklama
web/
  EKRANLAR.md                    ← ekran listesi, durumlar, bileşenler
```

`ai-service/` ve `web/` altındakiler **taslak ve öneri** — senin alanın, istediğin gibi değiştir. `contracts/` ise ortak alan: değişiklik önerirsen PR açalım, ikimiz onaylayınca geçsin.

## 4. Claude'u nasıl kurarsın (5 dakika)

1. claude.ai'de yeni bir **Project** oluştur: "Mülakat Simülatörü — AI & UI".
2. Proje bilgisine (knowledge) şunları yükle: `docs/PROJE_BAGLAMI.md`, `contracts/` içindeki her şey, `ai-service/rubrics/competencies.yaml`.
3. Proje talimatına, sana ayrıca gönderdiğim proje talimatı metnini yapıştır (repoda tutulmuyor).
4. Sözleşme her değiştiğinde proje bilgisindeki kopyayı güncelle (ben de kendi tarafımda aynısını yapacağım).

Böylece senin Claude'un ile benim Claude'um aynı mesaj formatlarını, aynı alan adlarını bilir.

## 5. İlk hafta (Faz 0) — senden beklenenler

- [ ] Bu klasörü oku, özellikle `contracts/ai-service-api.md`. Mantıksız gelen her şeyi işaretle.
- [ ] Aşağıdaki açık kararlar için fikrini söyle.
- [ ] `ai-service/` iskeleti: FastAPI, `/health`, `/v1/personas`, şemalara uyan sahte `/v1/plan`, `/v1/turn`, `/v1/report`.
- [ ] `web/` iskeleti: Next.js + TypeScript, giriş sayfası ve boş mülakat ekranı.
- [ ] Personalardan 2'sini gerçek prompt'larla deneyip komut satırında konuş.

Benim aynı hafta yapacaklarım: monorepo, `docker-compose.yml` (postgres, redis, minio, backend, ai-service, web), .NET iskeleti, `FakeAiClient`, ve tarayıcıya sahte olay yollayan bir test hub'ı. Hafta sonunda `docker compose up` ile her şeyin ayağa kalktığını birlikte görelim.

## 6. Birlikte karar vereceklerimiz (önerim parantez içinde)

1. AI servisi dili → **Python + FastAPI** (senin rahat ettiğin başka bir şey varsa söyle)
2. Arayüz → **önce web (Next.js, PWA)**, mobil sonra Expo ile — yoksa Flutter mı?
3. LLM → **Claude**; canlı turlarda hızlı model, raporda güçlü model
4. STT/TTS → Azure Speech ile başlarım, Faz 2'de karşılaştırırım
5. MVP dili → Türkçe + İngilizce birlikte mi, önce Türkçe mi?
6. Haftalık senkron günü/saati

## 7. Çalışma kuralları (kısa)

- `main` korumalı, dallar `feature/<alan>-<konu>` (ör. `feature/ai-persona-loader`, `feature/backend-auth`), PR ile birleşir.
- Birbirimizin PR'larını inceleriz.
- Kararlar `docs/adr/` altına 5–10 satırlık not.
- Loglara kullanıcı metni / CV yazmıyoruz (KVKK).

Sorun olursa ya da bir şey saçma geldiyse çekinmeden söyle — sözleşmeler şu an taslak, en ucuz değiştirme zamanı şimdi. 🙂
