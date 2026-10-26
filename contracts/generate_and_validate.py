"""Generates contracts/schemas/*.schema.json and contracts/examples/*.json, then validates examples."""
import json, os, sys
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = sys.argv[1]
SD = os.path.join(ROOT, "contracts", "schemas")
ED = os.path.join(ROOT, "contracts", "examples")
os.makedirs(SD, exist_ok=True); os.makedirs(ED, exist_ok=True)
BASE = "https://mulakat-sim.local/schemas/"

def sch(name, title, body):
    s = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": BASE + name, "title": title}
    s.update(body); return s

uuid = {"type": "string", "minLength": 1}
lang = {"enum": ["tr", "en"]}
loc = {"type": "object", "required": ["tr", "en"], "properties": {"tr": {"type": "string"}, "en": {"type": "string"}}, "additionalProperties": False}
competency_id = {"enum": ["communication", "problem_solving", "technical_depth", "ownership", "teamwork", "motivation_fit", "structure", "learning_agility"]}
qtype = {"enum": ["warmup", "behavioral", "technical", "situational", "cv_deep_dive", "job_requirement", "coding", "closing"]}

common = sch("common.schema.json", "Ortak tanımlar", {"$defs": {
    "uuid": uuid, "language": lang, "localized": loc, "competency_id": competency_id,
    "mode": {"enum": ["text", "voice"]},
    "profile": {"type": "object", "required": ["role", "level"], "additionalProperties": False, "properties": {
        "role": {"type": "string", "minLength": 1, "maxLength": 100},
        "level": {"enum": ["intern", "junior", "mid", "senior"]},
        "technologies": {"type": "array", "items": {"type": "string"}, "maxItems": 20}}},
    "turn_metrics": {"type": "object", "additionalProperties": False, "required": ["word_count"], "properties": {
        "duration_ms": {"type": ["integer", "null"], "minimum": 0},
        "word_count": {"type": "integer", "minimum": 0},
        "wpm": {"type": ["number", "null"], "minimum": 0},
        "filler_count": {"type": ["integer", "null"], "minimum": 0},
        "fillers": {"type": ["object", "null"], "additionalProperties": {"type": "integer", "minimum": 0}},
        "long_pause_count": {"type": ["integer", "null"], "minimum": 0},
        "longest_pause_ms": {"type": ["integer", "null"], "minimum": 0},
        "time_to_first_word_ms": {"type": ["integer", "null"], "minimum": 0}}},
    "history_item": {"type": "object", "required": ["index", "speaker", "text"], "additionalProperties": False, "properties": {
        "index": {"type": "integer", "minimum": 0},
        "speaker": {"enum": ["interviewer", "candidate"]},
        "text": {"type": "string"},
        "question_id": {"type": ["string", "null"]},
        "interrupted_at_char": {"type": ["integer", "null"], "minimum": 0}}},
    "session_metrics": {"type": "object", "additionalProperties": False, "required": ["total_duration_ms"], "properties": {
        "total_duration_ms": {"type": "integer", "minimum": 0},
        "candidate_talk_ratio": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
        "avg_wpm": {"type": ["number", "null"]},
        "filler_per_min": {"type": ["number", "null"]},
        "top_fillers": {"type": ["object", "null"], "additionalProperties": {"type": "integer"}},
        "long_pause_count": {"type": ["integer", "null"]},
        "avg_time_to_first_word_ms": {"type": ["integer", "null"]}}},
    "error": {"type": "object", "required": ["code", "message", "retryable"], "properties": {
        "code": {"type": "string"}, "message": {"type": "string"}, "retryable": {"type": "boolean"}}}}})
C = "common.schema.json#/$defs/"
r = lambda d: {"$ref": C + d}

persona = sch("persona.schema.json", "Persona (katalog girdisi)", {"type": "object", "additionalProperties": False,
    "required": ["id", "version", "display_name", "short_description", "interview_types", "difficulty", "languages", "competencies"],
    "properties": {
        "id": {"type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$"},
        "version": {"type": "integer", "minimum": 1},
        "display_name": r("localized"), "short_description": r("localized"),
        "interview_types": {"type": "array", "minItems": 1, "items": {"enum": ["hr", "behavioral", "technical", "system_design", "coding", "stress"]}},
        "difficulty": {"type": "integer", "minimum": 1, "maximum": 5},
        "languages": {"type": "array", "minItems": 1, "items": r("language")},
        "voice": {"type": "object", "properties": {"tr": {"type": "string"}, "en": {"type": "string"}}},
        "competencies": {"type": "array", "minItems": 1, "items": r("competency_id")}}})
persona_list = sch("persona-list.schema.json", "GET /v1/personas cevabı", {"type": "array", "items": {"$ref": "persona.schema.json"}})

plan_request = sch("plan-request.schema.json", "POST /v1/plan isteği", {"type": "object", "additionalProperties": False,
    "required": ["interview_id", "persona_id", "persona_version", "language", "mode", "duration_min", "profile"],
    "properties": {"interview_id": r("uuid"), "persona_id": {"type": "string"}, "persona_version": {"type": "integer"},
        "language": r("language"), "mode": r("mode"), "duration_min": {"type": "integer", "minimum": 10, "maximum": 45},
        "profile": r("profile"),
        "cv_text": {"type": ["string", "null"], "maxLength": 20000},
        "job_posting_text": {"type": ["string", "null"], "maxLength": 20000}}})

question = {"type": "object", "additionalProperties": False,
    "required": ["id", "type", "text", "competency_ids", "difficulty", "expected_points", "max_follow_ups"],
    "properties": {"id": {"type": "string", "pattern": "^q[0-9]+$"}, "type": qtype, "text": {"type": "string", "minLength": 5},
        "competency_ids": {"type": "array", "minItems": 1, "items": r("competency_id")},
        "difficulty": {"type": "integer", "minimum": 1, "maximum": 5},
        "expected_points": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
        "max_follow_ups": {"type": "integer", "minimum": 0, "maximum": 3}}}
plan = sch("plan.schema.json", "Mülakat planı", {"type": "object", "additionalProperties": False,
    "required": ["plan_version", "estimated_duration_min", "competencies", "questions"],
    "properties": {"plan_version": {"type": "integer", "minimum": 1},
        "estimated_duration_min": {"type": "integer", "minimum": 5, "maximum": 60},
        "competencies": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False,
            "required": ["id", "weight"], "properties": {"id": r("competency_id"), "weight": {"type": "number", "exclusiveMinimum": 0, "maximum": 1}}}},
        "questions": {"type": "array", "minItems": 3, "maxItems": 15, "items": question}}})

turn_request = sch("turn-request.schema.json", "POST /v1/turn isteği", {"type": "object", "additionalProperties": False,
    "required": ["interview_id", "persona_id", "persona_version", "language", "mode", "profile", "plan", "state", "history", "candidate_turn"],
    "properties": {"interview_id": r("uuid"), "persona_id": {"type": "string"}, "persona_version": {"type": "integer"},
        "language": r("language"), "mode": r("mode"), "profile": r("profile"), "plan": {"$ref": "plan.schema.json"},
        "state": {"type": "object", "additionalProperties": False,
            "required": ["current_question_id", "follow_ups_used", "asked_question_ids", "elapsed_sec", "remaining_sec", "token_budget_remaining"],
            "properties": {"current_question_id": {"type": ["string", "null"]}, "follow_ups_used": {"type": "integer", "minimum": 0},
                "asked_question_ids": {"type": "array", "items": {"type": "string"}},
                "elapsed_sec": {"type": "integer", "minimum": 0}, "remaining_sec": {"type": "integer"},
                "token_budget_remaining": {"type": "integer"}}},
        "history": {"type": "array", "items": r("history_item")},
        "candidate_turn": {"oneOf": [{"type": "null"}, {"type": "object", "additionalProperties": False,
            "required": ["index", "text", "metrics"], "properties": {"index": {"type": "integer"}, "text": {"type": "string", "maxLength": 8000},
                "metrics": r("turn_metrics")}}]}}})

turn_final = sch("turn-final.schema.json", "SSE 'final' olayı verisi", {"type": "object", "additionalProperties": False,
    "required": ["text", "decision", "usage"], "properties": {"text": {"type": "string", "minLength": 1},
        "decision": {"type": "object", "additionalProperties": False, "required": ["action", "question_id"], "properties": {
            "action": {"enum": ["follow_up", "next_question", "wrap_up", "end"]},
            "question_id": {"type": ["string", "null"]}, "reason": {"type": "string", "maxLength": 300}}},
        "usage": {"type": "object", "required": ["input_tokens", "output_tokens", "model"], "properties": {
            "input_tokens": {"type": "integer"}, "output_tokens": {"type": "integer"}, "model": {"type": "string"},
            "cache_read_tokens": {"type": "integer"}}}}})

report_request = sch("report-request.schema.json", "POST /v1/report isteği", {"type": "object", "additionalProperties": False,
    "required": ["interview_id", "persona_id", "persona_version", "language", "mode", "profile", "plan", "history", "session_metrics"],
    "properties": {"interview_id": r("uuid"), "persona_id": {"type": "string"}, "persona_version": {"type": "integer"},
        "language": r("language"), "mode": r("mode"), "profile": r("profile"), "plan": {"$ref": "plan.schema.json"},
        "history": {"type": "array", "minItems": 1, "items": r("history_item")}, "session_metrics": r("session_metrics")}})

report = sch("report.schema.json", "Mülakat raporu", {"type": "object", "additionalProperties": False,
    "required": ["rubric_version", "language", "overall_score", "summary", "competency_scores", "question_feedback", "speech_feedback", "next_steps"],
    "properties": {"rubric_version": {"type": "integer"}, "language": r("language"),
        "overall_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "summary": {"type": "string", "minLength": 10, "maxLength": 600},
        "competency_scores": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False,
            "required": ["competency_id", "score", "comment", "evidence"], "properties": {
                "competency_id": r("competency_id"), "score": {"type": "integer", "minimum": 1, "maximum": 5},
                "comment": {"type": "string", "maxLength": 400},
                "evidence": {"type": "array", "minItems": 1, "items": {"type": "object", "additionalProperties": False,
                    "required": ["turn_index", "quote"], "properties": {"turn_index": {"type": "integer", "minimum": 0}, "quote": {"type": "string", "maxLength": 200}}}}}}},
        "question_feedback": {"type": "array", "items": {"type": "object", "additionalProperties": False,
            "required": ["question_id", "strengths", "improvements", "better_answer_example", "star"], "properties": {
                "question_id": {"type": "string"}, "strengths": {"type": "array", "items": {"type": "string"}},
                "improvements": {"type": "array", "items": {"type": "string"}},
                "better_answer_example": {"type": ["string", "null"], "maxLength": 1200},
                "star": {"oneOf": [{"type": "null"}, {"type": "object", "additionalProperties": False,
                    "required": ["situation", "task", "action", "result"],
                    "properties": {k: {"type": "boolean"} for k in ["situation", "task", "action", "result"]}}]}}}},
        "speech_feedback": {"type": "object", "required": ["comments"], "properties": {"comments": {"type": "array", "items": {"type": "string"}}}},
        "language_feedback": {"type": ["object", "null"], "description": "Faz 4: İngilizce mülakatlarda dilbilgisi/kelime notları"},
        "next_steps": {"type": "array", "minItems": 1, "maxItems": 5, "items": {"type": "string"}}}})

event_types = ["interview.state", "transcript.partial", "turn.user.final", "interviewer.delta", "interviewer.final",
               "interviewer.interrupted", "metrics.update", "report.ready", "error"]
envelope = sch("hub-envelope.schema.json", "SignalR OnEvent zarfı (camelCase)", {"type": "object", "additionalProperties": False,
    "required": ["type", "seq", "interviewId", "ts", "payload"], "properties": {
        "type": {"enum": event_types}, "seq": {"type": "integer", "minimum": 0},
        "interviewId": {"type": "string"}, "ts": {"type": "string", "format": "date-time"}, "payload": {"type": "object"}},
    "allOf": [
        {"if": {"properties": {"type": {"const": "interviewer.final"}}}, "then": {"properties": {"payload": {"type": "object",
            "required": ["turnIndex", "text", "questionId", "action"], "properties": {"action": {"enum": ["follow_up", "next_question", "wrap_up", "end"]}}}}}},
        {"if": {"properties": {"type": {"const": "interview.state"}}}, "then": {"properties": {"payload": {"type": "object",
            "required": ["status"], "properties": {"status": {"enum": ["created", "active", "paused", "completed", "reported", "failed", "deleted"]}}}}}},
        {"if": {"properties": {"type": {"const": "error"}}}, "then": {"properties": {"payload": {"type": "object", "required": ["code", "message", "retryable"]}}}}]})

schemas = {"common": common, "persona": persona, "persona-list": persona_list, "plan-request": plan_request, "plan": plan,
           "turn-request": turn_request, "turn-final": turn_final, "report-request": report_request, "report": report, "hub-envelope": envelope}
for n, s in schemas.items():
    with open(os.path.join(SD, f"{n}.schema.json"), "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2); f.write("\n")

# ---- examples ----
profile = {"role": "Backend Developer", "level": "junior", "technologies": ["C#", ".NET", "PostgreSQL"]}
ex_plan = {"plan_version": 1, "estimated_duration_min": 20,
  "competencies": [{"id": "technical_depth", "weight": 0.35}, {"id": "problem_solving", "weight": 0.25},
                   {"id": "communication", "weight": 0.2}, {"id": "ownership", "weight": 0.2}],
  "questions": [
    {"id": "q1", "type": "warmup", "text": "Kısaca kendinden ve son projenden bahseder misin?", "competency_ids": ["communication"], "difficulty": 1, "expected_points": ["rolü", "teknolojiler", "kendi katkısı"], "max_follow_ups": 1},
    {"id": "q2", "type": "technical", "text": "Bir API'de N+1 sorgu problemini nasıl fark eder ve çözersin?", "competency_ids": ["technical_depth", "problem_solving"], "difficulty": 3, "expected_points": ["N+1 tanımı", "profiling/log", "eager loading veya projection", "ölçüm"], "max_follow_ups": 2},
    {"id": "q3", "type": "behavioral", "text": "Bir hatayı canlıya çıkardığın bir zamanı anlatır mısın?", "competency_ids": ["ownership", "communication"], "difficulty": 2, "expected_points": ["durum", "ne yaptığı", "sonuç", "ders"], "max_follow_ups": 2},
    {"id": "q4", "type": "closing", "text": "Bize sormak istediğin bir şey var mı?", "competency_ids": ["motivation_fit"], "difficulty": 1, "expected_points": [], "max_follow_ups": 0}]}
history = [
  {"index": 0, "speaker": "interviewer", "text": "Merhaba, ben Kaan. Kısaca kendinden ve son projenden bahseder misin?", "question_id": "q1"},
  {"index": 1, "speaker": "candidate", "text": "Merhaba, Uludağ'da bilgisayar mühendisliği okuyorum, son projem bir kütüphane API'siydi."},
  {"index": 2, "speaker": "interviewer", "text": "Güzel. Bir API'de N+1 sorgu problemini nasıl fark eder ve çözersin?", "question_id": "q2", "interrupted_at_char": None}]
metrics = {"duration_ms": 41200, "word_count": 96, "wpm": 139.8, "filler_count": 5, "fillers": {"ıı": 3, "şey": 2},
           "long_pause_count": 1, "longest_pause_ms": 3100, "time_to_first_word_ms": 1800}
iid = "0192f6a4-7c1e-7b3a-9d2e-5f1a2b3c4d5e"
examples = {
  "plan-request": {"interview_id": iid, "persona_id": "tech-lead-backend", "persona_version": 1, "language": "tr", "mode": "voice",
                   "duration_min": 20, "profile": profile, "cv_text": None, "job_posting_text": None},
  "plan": ex_plan,
  "turn-request": {"interview_id": iid, "persona_id": "tech-lead-backend", "persona_version": 1, "language": "tr", "mode": "voice",
     "profile": profile, "plan": ex_plan,
     "state": {"current_question_id": "q2", "follow_ups_used": 0, "asked_question_ids": ["q1", "q2"], "elapsed_sec": 412, "remaining_sec": 788, "token_budget_remaining": 42000},
     "history": history, "candidate_turn": {"index": 3, "text": "Iıı şey, EF Core'da Include kullanarak ilişkili verileri tek sorguda çekerim.", "metrics": metrics}},
  "turn-request-opening": {"interview_id": iid, "persona_id": "tech-lead-backend", "persona_version": 1, "language": "tr", "mode": "text",
     "profile": profile, "plan": ex_plan,
     "state": {"current_question_id": None, "follow_ups_used": 0, "asked_question_ids": [], "elapsed_sec": 0, "remaining_sec": 1200, "token_budget_remaining": 60000},
     "history": [], "candidate_turn": None},
  "turn-final": {"text": "Include kullanmak iyi bir başlangıç. Peki bunun bir N+1 olduğunu ilk başta nasıl fark ederdin?",
     "decision": {"action": "follow_up", "question_id": "q2", "reason": "Tespit yöntemi anlatılmadı."},
     "usage": {"input_tokens": 3120, "output_tokens": 48, "model": "claude-haiku-5-5"}},
  "report-request": {"interview_id": iid, "persona_id": "tech-lead-backend", "persona_version": 1, "language": "tr", "mode": "voice",
     "profile": profile, "plan": ex_plan, "history": history + [{"index": 3, "speaker": "candidate", "text": "EF Core'da Include kullanarak ilişkili verileri tek sorguda çekerim."}],
     "session_metrics": {"total_duration_ms": 1184000, "candidate_talk_ratio": 0.62, "avg_wpm": 131.2, "filler_per_min": 4.1,
                         "top_fillers": {"ıı": 21, "şey": 9, "yani": 7}, "long_pause_count": 6, "avg_time_to_first_word_ms": 1650}},
  "report": {"rubric_version": 1, "language": "tr", "overall_score": 50,
     "summary": "Teknik temelin sağlam; cevapların ölçüm ve sonuç kısmında zayıflıyor.",
     "competency_scores": [
        {"competency_id": "technical_depth", "score": 3, "comment": "N+1'i doğru çözdün ama tespit yöntemini ancak sorulunca açıkladın.", "evidence": [{"turn_index": 3, "quote": "EF Core'da Include kullanarak"}]},
        {"competency_id": "communication", "score": 3, "comment": "Net ama kısa; bağlam vermeden çözüme atladın.", "evidence": [{"turn_index": 1, "quote": "son projem bir kütüphane API'siydi"}]}],
     "question_feedback": [{"question_id": "q2", "strengths": ["Çözümü doğru seçtin."], "improvements": ["Problemi nasıl ölçtüğünü baştan söyle."],
        "better_answer_example": "Önce loglarda aynı sorgunun döngü içinde tekrarlandığını görürüm; sonra Include veya projection ile tek sorguya indirip süreyi karşılaştırırım.", "star": None}],
     "speech_feedback": {"comments": ["Dakikada ~4 dolgu kelimesi var; en sık 'ıı'. Cevaba başlamadan bir saniye düşünmek bunu azaltır."]},
     "language_feedback": None,
     "next_steps": ["Teknik cevaplara 'nasıl fark ettim' adımıyla başla.", "Davranışsal sorularda sonucu sayıyla bitir."]},
  "persona-list": [{"id": "hr-generalist", "version": 1, "display_name": {"tr": "Elif — İK Uzmanı", "en": "Elif — HR Specialist"},
     "short_description": {"tr": "Sıcak ama dikkatli; motivasyon ve iletişim odaklı.", "en": "Warm but attentive; focuses on motivation and communication."},
     "interview_types": ["hr", "behavioral"], "difficulty": 2, "languages": ["tr", "en"], "voice": {"tr": "tr-TR-EmelNeural", "en": "en-US-JennyNeural"},
     "competencies": ["communication", "motivation_fit", "teamwork", "ownership", "structure"]}],
  "hub-envelope": {"type": "interviewer.final", "seq": 12, "interviewId": iid, "ts": "2026-10-26T09:14:03Z",
     "payload": {"turnIndex": 4, "text": "Peki bunun bir N+1 olduğunu nasıl fark ederdin?", "questionId": "q2", "action": "follow_up"}},
}
ex_schema = {"turn-request-opening": "turn-request"}

reg = Registry().with_resources([(s["$id"], Resource.from_contents(s)) for s in schemas.values()])
ok = True
for n, ex in examples.items():
    sname = ex_schema.get(n, n)
    v = Draft202012Validator(schemas[sname], registry=reg)
    errs = list(v.iter_errors(ex))
    print(f"{n:24s} -> {sname:16s}", "OK" if not errs else f"FAIL: {[e.message for e in errs][:3]}")
    ok &= not errs
    with open(os.path.join(ED, f"{n}.json"), "w", encoding="utf-8") as f:
        json.dump(ex, f, ensure_ascii=False, indent=2); f.write("\n")

# business rules
w = sum(c["weight"] for c in ex_plan["competencies"]); assert abs(w - 1) < 0.01, w
rep = examples["report"]; wmap = {c["id"]: c["weight"] for c in ex_plan["competencies"]}
scored = [c for c in rep["competency_scores"] if c["competency_id"] in wmap]
tw = sum(wmap[c["competency_id"]] for c in scored)
calc = round((sum(wmap[c["competency_id"]] * c["score"] for c in scored) / tw - 1) / 4 * 100)
print("overall_score check:", calc, rep["overall_score"])
sys.exit(0 if ok and calc == rep["overall_score"] else 1)
