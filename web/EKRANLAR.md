# Web arayüzü — ekranlar ve durumlar (öneri)

> Şule'nin alanı; bu liste sadece başlangıç. Veri alan adları `contracts/rest-api.md` ve `contracts/realtime-hub.md` ile aynı.
> Mobil öncelikli tasarla (PWA); sesli mod telefonda çok kullanılacak.

## Ekran haritası

| # | Ekran | Yol | Faz | Kullandığı uçlar |
|---|---|---|---|---|
| 1 | Karşılama | `/` | 1 | — |
| 2 | Kayıt / giriş + onaylar | `/auth` | 1 | `/auth/*` |
| 3 | Ana sayfa (geçmiş mülakatlar) | `/app` | 1 | `GET /interviews`, `GET /me` |
| 4 | Mülakat kurulumu (sihirbaz) | `/app/new` | 1 (CV adımı 2) | `GET /personas`, `POST /documents`, `POST /interviews` |
| 5 | Mikrofon testi | `/app/interview/[id]/check` | 2 | — |
| 6 | Canlı mülakat | `/app/interview/[id]` | 1 (yazılı), 2 (sesli) | hub |
| 7 | Rapor bekleniyor | `/app/interview/[id]/report` | 1 | `report.ready`, `GET …/report` (202) |
| 8 | Rapor | `/app/interview/[id]/report` | 1 | `GET …/report`, `…/transcript`, `…/report.pdf` |
| 9 | İlerleme | `/app/progress` | 3 | `GET /progress` |
| 10 | Ayarlar ve gizlilik | `/app/settings` | 1 | `PATCH /me`, `DELETE /me` |

## 2 · Kayıt ve onaylar

İki ayrı onay kutusu (ön işaretli değil):
- "Konuşmamın yapay zekâ ve ses hizmeti sağlayıcılarına (yurt dışı) aktarılmasına izin veriyorum" → `crossBorderTransfer`. Zorunlu; olmadan mülakat başlatılamaz, nedeni açıkça yazılır.
- "Ses kayıtlarımın 30 gün saklanmasına izin veriyorum (raporda dinleyebilmek için)" → `audioStorage`. İsteğe bağlı.

Aydınlatma metnine link.

## 4 · Kurulum sihirbazı (4 adım)

1. **Rol ve seviye:** serbest metin rol (önerilerle), seviye seçimi, teknoloji etiketleri.
2. **Persona:** kartlar (ad, kısa açıklama, zorluk göstergesi, dil). `stress-interviewer` seçilince uyarı: "Bu mülakatçı bilinçli olarak sert davranır. İstediğin an bitirebilirsin."
3. **Bağlam (isteğe bağlı, Faz 2):** CV yükle / iş ilanı yapıştır. Yükleme sonrası `maskedFields` gösterilir: "Telefon ve e-postan gizlendi."
4. **Mod ve süre:** yazılı / sesli, 10–45 dk, dil. "Başlat" → `POST /interviews` (5–15 sn sürebilir: "Mülakatçın hazırlanıyor…").

## 6 · Canlı mülakat (en önemli ekran)

Ortak:
- Üstte: persona adı/avatarı, ilerleme (`currentQuestionIndex / totalQuestions`), kalan süre, Duraklat, Bitir.
- Ortada: sohbet akışı. Mülakatçı metni `interviewer.delta` geldikçe yazılır (daktilo efekti doğal olarak oluşur).
- Bağlantı göstergesi; koparsa "Yeniden bağlanılıyor…" ve otomatik `JoinInterview(id, lastSeq)`.

Yazılı mod:
- Altta metin kutusu (≤ 4000 karakter), Enter ile gönder, Shift+Enter yeni satır.
- Mülakatçı yazarken gönder düğmesi pasif.

Sesli mod:
- Büyük mikrofon/dalga göstergesi; mülakatçı konuşurken farklı renk.
- Canlı altyazı (`transcript.partial`), kapatılabilir.
- Mülakatçı konuşurken kullanıcı konuşursa: oynatmayı hemen kes, `Interrupt(playedMs)` gönder.
- İsteğe bağlı küçük göstergeler (`metrics.update`): hız ve dolgu kelimesi sayısı. **Varsayılan kapalı** — mülakat sırasında dikkat dağıtabilir; ayarlardan açılır.
- "Yazmaya geç" düğmesi (ortam gürültülüyse).

Kenar durumlar:
- `stt_failed` → "Sesini anlayamadık. Tekrar dene ya da yazılı moda geç."
- `ai_unavailable` → tur tekrar düğmesi.
- `budget_exhausted` / süre bitti → kapanış ekranı, rapora yönlendirme.
- Sekme kapanmak üzereyken onay ("Mülakat devam ediyor").

## 8 · Rapor

Yukarıdan aşağı:
1. Genel puan (0–100) + `summary`.
2. Yetkinlik kartları: puan (1–5), yorum, kanıt alıntısı. Alıntıya tıklayınca transkriptte o tura kayar; ses varsa o anı çalar (Faz 3).
3. Soru bazlı geri bildirim: güçlü yanlar, gelişim alanları, "daha iyi cevap" (açılır), STAR rozetleri (S/T/A/R yeşil/gri).
4. Konuşma: WPM, dakikada dolgu kelimesi, en sık dolgular, uzun sessizlikler + `speech_feedback`.
5. Sonraki adımlar (işaretlenebilir liste).
6. Eylemler: PDF indir, aynı ayarlarla tekrar dene, (Faz 4) mentora paylaş.

## 9 · İlerleme

- Yetkinlik başına zaman içindeki puan çizgisi.
- Dakikada dolgu kelimesi trendi.
- "En zayıf yetkinliğin: X — buna odaklı bir mülakat başlat" düğmesi (kurulumu o yetkinliğe uygun personayla doldurur).

## Bileşen önerileri

- Ses kaydı: `AudioWorklet` ile 16 kHz PCM16'ya örnekleme; VAD için `@ricky0123/vad-web` (Silero) değerlendirilebilir.
- Ses çalma: `AudioContext` + parça kuyruğu (24 kHz PCM16).
- Tipler: `openapi-typescript` ile REST tipleri; hub tipleri `contracts/schemas/hub-envelope.schema.json`'dan.
- Erişilebilirlik: altyazı her zaman mevcut, klavye ile tam kullanım, kontrast.
