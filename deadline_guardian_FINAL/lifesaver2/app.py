"""
DEADLINE GUARDIAN — Flask Backend  (google-genai SDK)
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import google.genai as genai
from agents.guardian import DeadlineGuardianAgent, clean_json

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
_client = genai.Client(api_key=GEMINI_API_KEY)


def _gen(prompt: str, max_tokens: int = 1024) -> str:
    """Single-turn Gemini call — returns text."""
    from google.genai import types
    resp = _client.models.generate_content(
        model="gemini-1.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=0.4,
        ),
    )
    return resp.text


def now_str() -> str:
    return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Agent (multi-step loop) ───────────────────────────────────────────────────

@app.route("/api/agent/run", methods=["POST"])
def agent_run():
    data         = request.json or {}
    tasks        = data.get("tasks", [])
    history      = data.get("history", [])
    user_request = data.get("request",
        "Analyse my task situation and give me a full action plan.")
    user_context = data.get("user_context", {"name": "User", "energy": "morning_peak"})

    try:
        agent  = DeadlineGuardianAgent(api_key=GEMINI_API_KEY)
        result = agent.run(user_request, tasks, history, user_context)
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── Fast single-call endpoints ────────────────────────────────────────────────

@app.route("/api/quick/prioritize", methods=["POST"])
def quick_prioritize():
    data  = request.json or {}
    tasks = [t for t in data.get("tasks", []) if not t.get("done")]
    if not tasks:
        return jsonify({"error": "No tasks"}), 400

    task_str = "\n".join(
        f"- ID:{t['id']} | {t['name']} | deadline:{t['deadline']} "
        f"| est:{t.get('hours',1)}h | cat:{t.get('category','?')}"
        for t in tasks
    )
    prompt = (
        f"Now is {now_str()}.\n"
        f"Rank these tasks. Return ONLY a JSON array, no markdown:\n"
        f'[{{"id":<id>,"priority":"Critical|High|Medium|Low","score":<1-100>,'
        f'"reason":"<15 words>","start_by":"<e.g. Now / In 2h>",'
        f'"next_action":"<specific first step>"}}]\n'
        f"Sort by score descending.\nTasks:\n{task_str}"
    )
    try:
        result = clean_json(_gen(prompt))
        return jsonify({"prioritized": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/quick/schedule", methods=["POST"])
def quick_schedule():
    data  = request.json or {}
    tasks = [t for t in data.get("tasks", []) if not t.get("done")]
    wake  = data.get("wake",  "07:00")
    sleep = data.get("sleep", "23:00")
    prefs = data.get("prefs", "")

    task_str = "\n".join(
        f"- {t['name']} | priority:{t.get('priority','M')} "
        f"| {t.get('hours',1)}h | dl:{t['deadline']}"
        for t in tasks
    )
    prompt = (
        f"Today {now_str()}. Awake {wake} to {sleep}. Prefs: {prefs or 'none'}.\n"
        f"Build hour-by-hour schedule. Return ONLY a JSON array, no markdown:\n"
        f'[{{"time":"9:00 AM","end_time":"10:30 AM",'
        f'"type":"work|break|meal|buffer","task":"<name>",'
        f'"notes":"<tip>","energy":"high|med|low"}}]\n'
        f"Place high-cognitive tasks at peak energy. Include 3 breaks minimum.\n"
        f"Tasks:\n{task_str}"
    )
    try:
        result = clean_json(_gen(prompt))
        return jsonify({"schedule": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/quick/breakdown", methods=["POST"])
def quick_breakdown():
    data = request.json or {}
    task = data.get("task", {})
    prompt = (
        f"Break this task into 20-40 min subtasks. Return ONLY a JSON array, no markdown:\n"
        f'[{{"order":<n>,"subtask":"<action verb + specific>",'
        f'"duration_min":<int>,"tip":"<1 line>","type":"thinking|doing|reviewing"}}]\n'
        f"Max 8 subtasks. Be specific.\n"
        f"Task: {task.get('name')} | desc: {task.get('description','')} "
        f"| est: {task.get('hours',2)}h"
    )
    try:
        result = clean_json(_gen(prompt))
        return jsonify({"subtasks": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/quick/procrastination", methods=["POST"])
def quick_procrastination():
    data    = request.json or {}
    history = data.get("history", [])
    if not history:
        return jsonify({
            "score":   30,
            "pattern": "No history yet",
            "insight": "Add tasks and mark them done to build your pattern profile.",
            "worst_time": "Unknown",
            "best_category":  "Unknown",
            "worst_category": "Unknown",
            "recommendation": "Start tracking tasks now.",
        })
    hist_str = json.dumps(history[-20:])
    prompt = (
        f"Analyse this task completion history for procrastination patterns.\n"
        f"History: {hist_str}\n"
        f"Return ONLY JSON, no markdown:\n"
        f'{{"score":<0-100>,"pattern":"chronic|moderate|minimal",'
        f'"insight":"<2 sentences>",'
        f'"worst_time":"<when they procrastinate most>",'
        f'"best_category":"<on-time category>",'
        f'"worst_category":"<delayed category>",'
        f'"recommendation":"<one specific behaviour change>"}}'
    )
    try:
        result = clean_json(_gen(prompt))
        return jsonify(result)
    except Exception as e:
        return jsonify({"score": 30, "pattern": "Error", "insight": str(e)}), 500


@app.route("/api/quick/reminder", methods=["POST"])
def quick_reminder():
    data      = request.json or {}
    task      = data.get("task", {})
    hrs_left  = data.get("hours_left", 24)
    user_name = data.get("user_name", "there")
    prompt = (
        f"Smart reminder for {user_name}. "
        f"Task: {task.get('name')} | {hrs_left}h left | category: {task.get('category','?')}.\n"
        f"Return ONLY JSON, no markdown:\n"
        f'{{"urgency":"critical|high|normal",'
        f'"message":"<2 punchy sentences>",'
        f'"action":"<one specific next step>",'
        f'"emoji":"<1-2 emoji>"}}'
    )
    try:
        result = clean_json(_gen(prompt, max_tokens=256))
        return jsonify({"reminder": result})
    except Exception:
        return jsonify({"reminder": {
            "urgency": "normal",
            "message": f"Time to work on {task.get('name','your task')}!",
            "action":  "Open your notes and start.",
            "emoji":   "⏰",
        }})


@app.route("/api/quick/voice-parse", methods=["POST"])
def quick_voice_parse():
    data = request.json or {}
    text = data.get("text", "")
    prompt = (
        f"Extract task details from this voice input. Today is {now_str()}.\n"
        f'Voice: "{text}"\n'
        f"Return ONLY JSON, no markdown:\n"
        f'{{"name":"<task name>",'
        f'"deadline":"<ISO datetime — infer from \'tomorrow\'/\'in 3 hours\' etc>",'
        f'"category":"Academic|Work|Personal|Health|Finance|Other",'
        f'"hours":<estimated hours>,"detected":true}}\n'
        f'If no task detected, return {{"detected":false}}'
    )
    try:
        result = clean_json(_gen(prompt, max_tokens=256))
        return jsonify(result)
    except Exception:
        return jsonify({"detected": False})


@app.route("/api/quick/coach", methods=["POST"])
def quick_coach():
    data       = request.json or {}
    tasks      = data.get("tasks", [])
    user_name  = data.get("user_name", "there")
    situation  = data.get("situation", "")
    active     = [t for t in tasks if not t.get("done")]
    done_today = [t for t in tasks if t.get("done")]
    overview   = json.dumps(
        [{"name": t["name"], "deadline": t.get("deadline")} for t in active[:5]]
    )
    prompt = (
        f"You are a tough-love productivity coach. Be direct, not generic.\n"
        f"User: {user_name} | Time: {now_str()}\n"
        f"Active: {len(active)} tasks | Done today: {len(done_today)}\n"
        f"Situation: {situation or 'General check-in'}\n"
        f"Tasks: {overview}\n"
        f"Give a SHORT punchy coach message (3-4 sentences). Specific to their situation.\n"
        f"Return ONLY JSON, no markdown:\n"
        f'{{"coach_message":"<message>","mood":"motivating|warning|celebrating|urgent",'
        f'"tip":"<one specific action>"}}'
    )
    try:
        result = clean_json(_gen(prompt, max_tokens=256))
        return jsonify(result)
    except Exception:
        return jsonify({
            "coach_message": "Focus on what matters most right now.",
            "mood":          "motivating",
            "tip":           "Pick your #1 task and work on it for 25 minutes.",
        })


@app.route("/api/calendar/sync", methods=["POST"])
def calendar_sync():
    """Simulated Google Calendar conflict check.
    Production: replace simulated_events with real Google Calendar API v3 call."""
    data  = request.json or {}
    tasks = [t for t in data.get("tasks", []) if not t.get("done")]
    now   = datetime.now()

    simulated_events = [
        {"title": "Team standup",     "start": now.replace(hour=10, minute=0).isoformat(), "duration_min": 30},
        {"title": "Lunch",            "start": now.replace(hour=13, minute=0).isoformat(), "duration_min": 60},
        {"title": "1-on-1 with manager", "start": now.replace(hour=15, minute=0).isoformat(), "duration_min": 45},
    ]
    busy_hrs         = sum(e["duration_min"] for e in simulated_events) / 60
    free_hrs         = max(0.0, 8.0 - busy_hrs)
    active_task_hrs  = sum(float(t.get("hours", 1)) for t in tasks)
    overcommitted    = active_task_hrs > free_hrs

    prompt = (
        f"Calendar shows {busy_hrs}h of meetings today. {free_hrs}h free.\n"
        f"User has {active_task_hrs}h of task work needed.\n"
        f"Tasks: {[t['name'] for t in tasks]}\n"
        f"Events: {[e['title'] for e in simulated_events]}\n"
        f"Return ONLY JSON, no markdown:\n"
        f'{{"overcommitted":{str(overcommitted).lower()},'
        f'"free_hours":{free_hrs},"busy_hours":{busy_hrs},'
        f'"recommendation":"<2 sentences>",'
        f'"reschedule_suggestions":[{{"task":"<name>","suggest":"<when>"}}]}}'
    )
    try:
        result = clean_json(_gen(prompt, max_tokens=512))
    except Exception:
        result = {
            "overcommitted":          overcommitted,
            "free_hours":             free_hrs,
            "busy_hours":             busy_hrs,
            "recommendation":         "Check your calendar and adjust task deadlines accordingly.",
            "reschedule_suggestions": [],
        }
    result["calendar_events"] = simulated_events
    return jsonify(result)


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
