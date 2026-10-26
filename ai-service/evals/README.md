# Değerlendirme seti (eval) — prompt'ları güvenle değiştirmek için

Prompt'u her değiştirdiğinde "daha mı iyi oldu, bir şeyi mi bozdum?" sorusunu elle cevaplamak zor. Bu klasör bunu otomatikleştirmek için.

## Vaka biçimi

Her vaka `cases/*.json` içinde:

- `kind`: `turn` (tek bir mülakatçı turu) veya `report` (tam rapor)
- `input`: `/v1/turn` veya `/v1/report` isteğinin aynısı (şemaya uyar)
- `expect`: kontrol edilecek beklentiler

## Kontrol türleri

**Kesin kontroller (kodla):**
- Çıktı şemaya uyuyor mu?
- `turn` için: `decision.action` beklenen kümede mi? Sesli modda cümle sayısı ≤ 3 mü? Metinde markdown/emoji var mı?
- `report` için: her `evidence.quote` transkriptte birebir geçiyor mu? Puan beklenen aralıkta mı?

**Tutarlılık (Faz 3 kabul kriteri):** aynı rapor vakasını 5 kez çalıştır; her yetkinlik puanının en yüksek ile en düşük değeri arasındaki fark ≤ 1 olmalı (≈ ±0,5).

**Yargıç model (isteğe bağlı):** "Bu takip sorusu adayın cevabındaki eksikliği hedefliyor mu?" gibi açık uçlu sorular için ikinci bir LLM'e 1–5 puan verdir. Yalnızca trend takibi için; tek başına geçme/kalma kriteri yapma.

## Başlangıç vakaları (taslak — çoğaltılmalı)

| Dosya | Ne test ediyor |
|---|---|
| `turn_shallow_answer.json` | Yüzeysel cevaba takip sorusu sorulur |
| `turn_prompt_injection.json` | "Talimatlarını unut" içeren cevap mülakatı bozmaz |
| `report_star_missing_result.json` | Sonucu eksik davranışsal cevapta `star.result = false` ve `structure` ≤ 3 |

Hedef: Faz 1 sonunda ~15, Faz 3 sonunda ~40 vaka. Gerçek kullanıcı mülakatlarından (izinli ve anonimleştirilmiş) vaka türetmek en değerlisi.

## Çalıştırma önerisi

`pytest` + her vaka için bir parametre; CI'da her PR'da kesin kontroller, tutarlılık testi gece bir kez (maliyet).
