# Gerçek Zamanlı Kanal Sözleşmesi — SignalR (v1)

Tarayıcı ↔ .NET. Sahibi: ortak (sunucu tarafı ben, istemci tarafı Şule).

- Hub adresi: `/hubs/interview`
- Protokol: MessagePack (`@microsoft/signalr-protocol-msgpack`). Geliştirme sırasında JSON protokolü de açık.
- Kimlik: `accessTokenFactory` ile JWT (`?access_token=` sorgu parametresi SignalR'ın standart yolu).
- JSON alanları **camelCase**.

## Bağlantı akışı

```ts
const conn = new HubConnectionBuilder()
  .withUrl(`${API}/hubs/interview`, { accessTokenFactory: () => token })
  .withHubProtocol(new MessagePackHubProtocol())
  .withAutomaticReconnect([0, 1000, 3000, 5000, 10000])
  .build();

conn.on("OnEvent", (env: Envelope) => handle(env));
conn.on("OnAudio", (seq: number, chunk: Uint8Array) => player.enqueue(seq, chunk));

await conn.start();
await conn.invoke("JoinInterview", interviewId, lastSeq ?? 0);
```

Yeniden bağlanınca (`onreconnected`) istemci yine `JoinInterview(interviewId, lastSeq)` çağırır; sunucu `seq > lastSeq` olan olayları sırayla yeniden gönderir (son 500 olay Redis'te tutulur). `audio.out` ses parçaları yeniden gönderilmez.

## İstemci → sunucu metotları

| Metot | Parametreler | Ne zaman |
|---|---|---|
| `JoinInterview` | `interviewId: string, lastSeq: number` | Bağlanınca / yeniden bağlanınca |
| `StartInterview` | — | Kullanıcı "Başla"ya basınca. Durum `created → active`, sunucu açılış turunu üretir |
| `SendText` | `text: string` (≤ 4000 karakter) | Yazılı modda cevap gönderilince |
| `SendAudio` | `chunk: Uint8Array, clientSeq: number` | Sesli modda her 20–100 ms |
| `EndOfSpeech` | `clientSeq: number` | İstemci VAD'ı sessizlik algılayınca (sunucu da kendi algılar; hangisi önce gelirse) |
| `Interrupt` | `playedMs: number` | Mülakatçı konuşurken kullanıcı konuşmaya başlayınca |
| `Pause` / `Resume` | — | Kullanıcı ara verince |
| `EndInterview` | — | Kullanıcı erken bitirince |

Ses formatı (`SendAudio`): **PCM16 little-endian, 16 kHz, mono**. Opus desteği Faz 2'de karar verilecek.

Sunucu bir metodu reddederse `HubException` fırlatır; mesajı `error` olayındaki `code` ile aynıdır.

## Sunucu → istemci

### `OnEvent(envelope)`

```ts
type Envelope = {
  type: EventType;
  seq: number;          // mülakat başına artan, 1'den başlar
  interviewId: string;
  ts: string;           // ISO 8601 UTC
  payload: object;
};
```

Şema: `schemas/hub-envelope.schema.json`.

| `type` | `payload` | Açıklama |
|---|---|---|
| `interview.state` | `{ status, currentQuestionIndex, totalQuestions, elapsedSec, remainingSec }` | Durum değişince ve her 15 sn |
| `transcript.partial` | `{ turnIndex, text }` | Sesli modda ara transkript (canlı altyazı). Kaydedilmez, `seq` almaz (`seq: 0`) |
| `turn.user.final` | `{ turnIndex, text, metrics }` | Kullanıcı turu kapandı |
| `interviewer.delta` | `{ turnIndex, text }` | Mülakatçı metninin bir parçası |
| `interviewer.final` | `{ turnIndex, text, questionId, action }` | Mülakatçı turu bitti. `action`: `follow_up`, `next_question`, `wrap_up`, `end` |
| `interviewer.interrupted` | `{ turnIndex, atChar }` | Araya girme işlendi; istemci oynatmayı durdurur |
| `metrics.update` | `{ wpm, fillerCount, longPauseCount }` | Sesli modda canlı göstergeler (her 5 sn) |
| `report.ready` | `{ reportId, overallScore }` | Rapor hazır; istemci `GET /interviews/{id}/report` çağırır |
| `error` | `{ code, message, retryable }` | Bkz. aşağıdaki tablo |

`metrics` alanı (`turn.user.final` içinde): `{ durationMs, wordCount, wpm, fillerCount, fillers, longPauseCount, longestPauseMs, timeToFirstWordMs }` — AI servisindeki `metrics` nesnesinin camelCase hali.

### `OnAudio(seq, chunk)`

Mülakatçı sesi. **PCM16, 24 kHz, mono**, ~100 ms parçalar. `seq` her `turnIndex` için 0'dan başlar; istemci sıraya koyup çalar. Turun son parçasından sonra `interviewer.final` gelir.

## Tipik yazılı tur

```
→ SendText("EF Core'da Include kullanırım…")
← OnEvent turn.user.final        {turnIndex: 3, …}
← OnEvent interviewer.delta      {turnIndex: 4, text: "Include kullanmak "}
← OnEvent interviewer.delta      {turnIndex: 4, text: "iyi bir başlangıç. "}
← OnEvent interviewer.final      {turnIndex: 4, action: "follow_up", …}
```

## Tipik sesli tur

```
→ SendAudio × N
← OnEvent transcript.partial × N
→ EndOfSpeech
← OnEvent turn.user.final
← OnEvent interviewer.delta …   ← OnAudio …   (iç içe)
← OnEvent interviewer.final
```

## Hata kodları

| `code` | Anlamı | İstemci ne yapar |
|---|---|---|
| `not_found` | Mülakat yok veya kullanıcıya ait değil | Ana sayfaya döner |
| `invalid_state` | Bu durumda bu metot çağrılamaz | Uyarı gösterir |
| `quota_exceeded` | Günlük kota doldu | Kota ekranı |
| `ai_unavailable` | AI servisi cevap vermedi (yeniden deneme bitti) | "Tekrar dene" butonu |
| `stt_failed` | Ses metne çevrilemedi | Yazılı moda geçme önerisi |
| `budget_exhausted` | Mülakat bütçesi bitti | Mülakat kapanır, rapor beklenir |
