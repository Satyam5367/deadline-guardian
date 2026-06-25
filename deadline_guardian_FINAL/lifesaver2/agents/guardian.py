"""
DEADLINE GUARDIAN — Agentic Core (google-genai SDK)
Real multi-step agent loop using Gemini 1.5 Pro function calling.
"""

import json
import re
from datetime import datetime, timedelta
import google.genai as genai
from google.genai import types

# ── Tool schemas ──────────────────────────────────────────────────────────────

TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="analyze_deadline_risk",
        description=(
            "Deeply analyze a task's deadline risk considering current time, "
            "complexity, and the user's historical procrastination score."
        ),
        parameters={
            "type": "object",
            "properties": {
                "task_name":            {"type": "string"},
                "deadline_iso":         {"type": "string"},
                "est_hours":            {"type": "number"},
                "category":             {"type": "string"},
                "procrastination_score":{"type": "number",
                                         "description": "0-100, user's delay tendency"},
            },
            "required": ["task_name", "deadline_iso", "est_hours"],
        },
    ),
    types.FunctionDeclaration(
        name="generate_micro_plan",
        description=(
            "Break a task into focused micro-sessions that fit the user's "
            "available time windows today."
        ),
        parameters={
            "type": "object",
            "properties": {
                "task_name":         {"type": "string"},
                "total_hours":       {"type": "number"},
                "available_slots":   {"type": "array", "items": {"type": "string"}},
                "energy_preference": {
                    "type": "string",
                    "enum": ["morning_peak", "afternoon", "night_owl"],
                },
            },
            "required": ["task_name", "total_hours", "available_slots"],
        },
    ),
    types.FunctionDeclaration(
        name="detect_conflict_cascade",
        description=(
            "Find all deadline conflicts across tasks and compute which ones "
            "cascade if any single task overruns."
        ),
        parameters={
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of active task objects",
                },
                "trigger_task_id": {
                    "type": "string",
                    "description": "Task that just changed (optional)",
                },
            },
            "required": ["tasks"],
        },
    ),
    types.FunctionDeclaration(
        name="compute_procrastination_pattern",
        description=(
            "Analyse task-completion history to identify procrastination "
            "patterns by category, time of day, and deadline proximity."
        ),
        parameters={
            "type": "object",
            "properties": {
                "history":         {"type": "array", "items": {"type": "object"}},
                "category_filter": {"type": "string"},
            },
            "required": ["history"],
        },
    ),
    types.FunctionDeclaration(
        name="generate_rescue_plan",
        description=(
            "Emergency plan when the user is in deadline crisis "
            "(< 20 % time remaining for remaining work)."
        ),
        parameters={
            "type": "object",
            "properties": {
                "overloaded_tasks": {"type": "array", "items": {"type": "object"}},
                "hours_available":  {"type": "number"},
                "stress_level":     {"type": "string", "enum": ["high", "critical"]},
            },
            "required": ["overloaded_tasks", "hours_available"],
        },
    ),
]

AGENT_TOOL = types.Tool(function_declarations=TOOL_DECLARATIONS)


# ── Tool execution (local, no extra API call) ─────────────────────────────────

def execute_tool(tool_name: str, args: dict, tasks: list, history: list) -> dict:
    now = datetime.now()

    if tool_name == "analyze_deadline_risk":
        raw_dl = args.get("deadline_iso", "")
        try:
            dl = datetime.fromisoformat(raw_dl.replace("Z", "").replace("+00:00", ""))
        except Exception:
            dl = now + timedelta(hours=24)
        hours_left    = max(0.0, (dl - now).total_seconds() / 3600)
        est           = float(args.get("est_hours", 1))
        proc_score    = float(args.get("procrastination_score", 30))
        buffer_ratio  = hours_left / max(est, 0.5)
        adj_ratio     = buffer_ratio / (1 + proc_score / 100)
        risk = (
            "CRITICAL" if adj_ratio < 1.2 else
            "HIGH"     if adj_ratio < 2.0 else
            "MEDIUM"   if adj_ratio < 4.0 else
            "LOW"
        )
        return {
            "risk_level": risk,
            "hours_remaining": round(hours_left, 1),
            "est_hours": est,
            "buffer_ratio": round(adj_ratio, 2),
            "procrastination_adjusted": True,
            "recommended_start": (
                "NOW" if risk == "CRITICAL"
                else f"Within {max(1, round(hours_left * 0.2))} hours"
            ),
            "survival_probability": min(99, max(5, round(adj_ratio * 25))),
        }

    if tool_name == "generate_micro_plan":
        task        = args.get("task_name", "Task")
        total       = float(args.get("total_hours", 2))
        slots       = args.get("available_slots") or ["09:00", "14:00", "19:00"]
        session_len = 0.75  # 45-min focused sessions
        sessions, remaining = [], total
        for slot in slots:
            if remaining <= 0:
                break
            dur = min(remaining, session_len)
            sessions.append({
                "start":        slot,
                "duration_min": round(dur * 60),
                "focus":        f"Session {len(sessions)+1}: {task}",
                "technique":    "Pomodoro" if dur <= 0.5 else "Deep Work",
                "goal":         f"Complete {round(dur / total * 100)}% of work",
            })
            remaining -= dur
        return {
            "sessions":          sessions,
            "total_sessions":    len(sessions),
            "recovery_possible": remaining <= 0,
        }

    if tool_name == "detect_conflict_cascade":
        active   = [t for t in tasks if not t.get("done")]
        sorted_t = sorted(active, key=lambda t: t.get("deadline", "9999"))
        conflicts, cumulative = [], 0.0
        for i, t in enumerate(sorted_t):
            cumulative += float(t.get("hours", 1))
            try:
                dl       = datetime.fromisoformat(t["deadline"].replace("T", " "))
                hrs_to_dl = (dl - now).total_seconds() / 3600
            except Exception:
                hrs_to_dl = 9999
            if cumulative > hrs_to_dl:
                conflicts.append({
                    "task":          t["name"],
                    "deadline":      t.get("deadline"),
                    "overrun_hours": round(cumulative - hrs_to_dl, 1),
                    "cascades_from": sorted_t[i - 1]["name"] if i > 0 else "current load",
                    "severity":      "CRITICAL" if cumulative - hrs_to_dl > 4 else "HIGH",
                })
        future_deadlines = []
        for t in active:
            try:
                dl = datetime.fromisoformat(t["deadline"].replace("T", " "))
                future_deadlines.append((dl - now).total_seconds() / 3600)
            except Exception:
                pass
        overcommit = round(
            max(0, cumulative - max(future_deadlines, default=0)), 1
        )
        return {
            "conflicts_found":            len(conflicts),
            "cascade_chain":              conflicts,
            "total_overcommitment_hours": overcommit,
        }

    if tool_name == "compute_procrastination_pattern":
        hist = args.get("history") or []
        if not hist:
            return {
                "pattern": "insufficient_data",
                "score":   30,
                "worst_category": "unknown",
            }
        delays, cat_delays = [], {}
        for h in hist:
            if h.get("completedAt") and h.get("deadline"):
                try:
                    completed = datetime.fromisoformat(h["completedAt"])
                    dl        = datetime.fromisoformat(h["deadline"].replace("T", " "))
                    delay_hrs = (completed - dl).total_seconds() / 3600
                    delays.append(delay_hrs)
                    cat = h.get("category", "General")
                    cat_delays.setdefault(cat, []).append(delay_hrs)
                except Exception:
                    pass
        avg_delay = sum(delays) / len(delays) if delays else 0
        score     = min(100, max(0, 50 + avg_delay * 5))
        worst_cat = (
            max(cat_delays, key=lambda c: sum(cat_delays[c]) / len(cat_delays[c]))
            if cat_delays else "Unknown"
        )
        return {
            "procrastination_score": round(score),
            "avg_delay_hours":       round(avg_delay, 1),
            "worst_category":        worst_cat,
            "total_tasks_analysed":  len(delays),
            "pattern": (
                "chronic"  if score > 70 else
                "moderate" if score > 40 else
                "minimal"
            ),
        }

    if tool_name == "generate_rescue_plan":
        crisis_tasks = sorted(
            args.get("overloaded_tasks") or [],
            key=lambda t: t.get("deadline", "9999"),
        )
        avail, plan, dropped = float(args.get("hours_available", 4)), [], []
        for t in crisis_tasks:
            needed = float(t.get("hours", 1))
            if avail >= needed * 0.6:
                alloc = min(avail, needed)
                plan.append({
                    "task":      t["name"],
                    "alloc_hrs": round(alloc, 1),
                    "action":    "DO NOW",
                    "mvp_scope": f"Core only ({round(alloc/needed*100)}% scope)",
                    "deadline":  t.get("deadline"),
                })
                avail -= alloc
            else:
                dropped.append({
                    "task":   t["name"],
                    "action": "DEFER or NEGOTIATE",
                    "reason": "Insufficient time",
                })
        return {
            "rescue_plan":  plan,
            "dropped_tasks": dropped,
            "mode":         "EMERGENCY",
            "message":      "Deadline crisis. Execute this plan NOW. No breaks > 5 min.",
        }

    return {"error": f"Unknown tool: {tool_name}"}


# ── Agent ──────────────────────────────────────────────────────────────────────

class DeadlineGuardianAgent:
    """
    Multi-step autonomous agent using Gemini 1.5 Pro function calling.
    Loop: think → call tool → observe → think again → conclude.
    """

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def run(
        self,
        user_request: str,
        tasks: list,
        history: list,
        user_context: dict,
    ) -> dict:
        now_str    = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        active     = [t for t in tasks if not t.get("done")]
        task_lines = "\n".join(
            f"- [{t.get('id')}] {t['name']} | deadline:{t.get('deadline','?')} "
            f"| est:{t.get('hours',1)}h | cat:{t.get('category','?')} "
            f"| priority:{t.get('priority','?')}"
            for t in active
        ) or "No active tasks."

        system = (
            f"You are Deadline Guardian — an autonomous AI productivity agent.\n"
            f"Current time: {now_str}\n"
            f"User: {user_context.get('name', 'User')} | "
            f"Energy: {user_context.get('energy', 'morning_peak')}\n\n"
            f"ACTIVE TASKS:\n{task_lines}\n\n"
            f"AGENT RULES:\n"
            f"1. ALWAYS call at least 2 tools before concluding.\n"
            f"2. If ANY deadline risk detected → call detect_conflict_cascade.\n"
            f"3. If completion history available → call compute_procrastination_pattern FIRST.\n"
            f"4. If workload > available time → call generate_rescue_plan.\n"
            f"5. Be brutally honest about risks.\n"
            f"6. End with a numbered, concrete action plan.\n"
        )

        contents       = [types.Content(role="user", parts=[types.Part(text=user_request)])]
        tool_calls     = []
        agent_steps    = []
        final_text     = "Analysis complete."
        max_iterations = 7

        for iteration in range(max_iterations):
            response = self.client.models.generate_content(
                model="gemini-1.5-pro",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    tools=[AGENT_TOOL],
                    max_output_tokens=2048,
                    temperature=0.4,
                ),
            )

            candidate = response.candidates[0]
            resp_parts = candidate.content.parts

            fn_calls, text_parts = [], []
            for part in resp_parts:
                if part.function_call and part.function_call.name:
                    fn_calls.append(part.function_call)
                elif part.text:
                    text_parts.append(part.text)

            if text_parts:
                agent_steps.append({
                    "type":    "reasoning",
                    "content": " ".join(text_parts),
                })

            if not fn_calls:
                final_text = " ".join(text_parts) if text_parts else final_text
                break

            # Append model turn
            contents.append(types.Content(role="model", parts=resp_parts))

            # Execute tools and build function-response parts
            fn_response_parts = []
            for fc in fn_calls:
                args   = dict(fc.args) if fc.args else {}
                result = execute_tool(fc.name, args, tasks, history)
                tool_calls.append({"tool": fc.name, "args": args, "result": result})
                agent_steps.append({
                    "type":   "tool_call",
                    "tool":   fc.name,
                    "result": result,
                })
                fn_response_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fc.name,
                            response=result,
                        )
                    )
                )

            contents.append(types.Content(role="user", parts=fn_response_parts))

        # Derive urgency
        urgency = "NORMAL"
        for tc in tool_calls:
            r = tc.get("result", {})
            if r.get("risk_level") == "CRITICAL" or r.get("conflicts_found", 0) > 0:
                urgency = "CRITICAL"
                break
            if r.get("risk_level") == "HIGH":
                urgency = "HIGH"

        return {
            "agent_steps":    agent_steps,
            "tool_calls_made": tool_calls,
            "final_analysis": final_text,
            "urgency_level":  urgency,
            "iterations":     iteration + 1,
        }


# ── Utility ────────────────────────────────────────────────────────────────────

def clean_json(raw: str):
    cleaned = raw.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned)
    cleaned = re.sub(r"^```\s*",     "", cleaned)
    cleaned = re.sub(r"```\s*$",     "", cleaned)
    return json.loads(cleaned.strip())
