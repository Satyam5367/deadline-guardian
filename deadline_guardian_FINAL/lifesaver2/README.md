# ⚡ Deadline Guardian — AI Productivity Agent

> The world's first truly **agentic** deadline management system. Powered by **Gemini 1.5 Pro function calling** — not just Q&A, but a real multi-step autonomous reasoning loop.

---

## 🚀 Live Demo

**[→ Open Live App](YOUR_DEPLOYED_URL_HERE)**

---

## 🤖 What Makes This Different

Every other productivity app gives you reminders you ignore. **Deadline Guardian** runs a real AI agent loop:

```
User adds task
      ↓
Agent THINKS → calls analyze_deadline_risk tool
      ↓
Agent OBSERVES result → calls detect_conflict_cascade tool
      ↓
Agent OBSERVES → calls compute_procrastination_pattern tool
      ↓
Agent SYNTHESIZES all results → outputs concrete rescue plan
      ↓
If new task added → autonomously reruns the loop
```

This is **Gemini function calling in a loop** — not a single API call.

---

## ✨ Features

| Feature | What it does |
|---------|-------------|
| 🤖 **Multi-Step AI Agent** | Gemini 1.5 Pro function calling loop — thinks, calls tools, observes, replans |
| ⚡ **Agentic Conflict Detection** | When any task is added, agent auto-detects cascading deadline conflicts |
| 🧠 **Procrastination AI** | Learns your delay patterns by category, time of day, deadline proximity |
| 🎯 **AI Task Prioritizer** | Ranks by urgency + impact + your personal procrastination score |
| 📅 **Smart Scheduler** | Energy-aware hourly plan (peaks for hard tasks, valleys for breaks) |
| 🔧 **Task Breakdown** | Splits any task into timed, typed subtasks (thinking/doing/reviewing) |
| 📆 **Calendar Conflict Check** | Detects when meetings eat your task time; suggests reschedules |
| 🔔 **Smart Reminders** | Context-aware, personalized nudges — not generic pings |
| 💬 **AI Coach** | Daily situation-aware motivational message |
| 🎙️ **Voice Input** | NLP-parsed voice → structured task (deadline, category, hours) |
| 🔥 **Habit Tracker** | 7-day grid with automatic streak tracking |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Core** | Gemini 1.5 Pro — function calling + multi-step loop |
| **Backend** | Python 3.11, Flask 3.0 |
| **Frontend** | HTML5, CSS3, Vanilla JS (single-page app) |
| **Deployment** | Google Cloud Run via Google AI Studio |
| **Voice** | Web Speech API (NLP-parsed by Gemini) |

### Google Technologies Used
- ✅ **Google AI Studio** — build and deploy platform
- ✅ **Gemini 1.5 Pro API** — function calling, multi-step agent loop
- ✅ **google-generativeai SDK** — Python integration
- ✅ **Google Cloud Run** — serverless deployment

---

## 📁 Project Structure

```
deadline-guardian/
├── app.py                    # Flask backend — all API routes
├── agents/
│   ├── __init__.py
│   └── guardian.py           # The real multi-step agent loop
├── requirements.txt
├── Dockerfile                # Cloud Run deployment
├── .env.example
├── templates/
│   └── index.html            # Full SPA frontend (dark theme)
└── README.md
```

---

## 🧠 The Agentic Architecture

```
┌─────────────────────────────────────────────────────┐
│                  DeadlineGuardianAgent               │
│                                                     │
│  User Request → Gemini 1.5 Pro (function calling)  │
│                        ↓                           │
│           ┌────────────────────────┐               │
│           │   Tool: analyze_risk   │               │
│           │   Tool: detect_cascade │               │
│           │   Tool: procrastination│               │
│           │   Tool: rescue_plan    │               │
│           │   Tool: micro_plan     │               │
│           └────────────────────────┘               │
│                        ↓                           │
│         Results feed back to Gemini (loop)         │
│                        ↓                           │
│              Final synthesis + action plan         │
└─────────────────────────────────────────────────────┘
```

---

## ⚙️ Local Setup

```bash
# 1. Clone
git clone https://github.com/Satyam5367/deadline-guardian.git
cd deadline-guardian

# 2. Install
pip install -r requirements.txt

# 3. Set API key
cp .env.example .env
# Edit .env → GEMINI_API_KEY=AIza...

# 4. Run
python app.py
# Open http://localhost:5000
```

Get your Gemini key: https://aistudio.google.com/apikey

---

## 🚀 Deploy to Google Cloud Run

```bash
gcloud run deploy deadline-guardian \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=AIza...yourkey \
  --timeout 180
```

Or use the 1-click deploy from **Google AI Studio → Build → Deploy**.

---

## 📊 Evaluation Criteria Mapping

| Criteria | Weight | Our Approach |
|---------|--------|--------------|
| Problem Solving & Impact | 20% | Moves beyond reminders — actively prevents missed deadlines |
| **Agentic Depth** | **20%** | **Real Gemini function calling loop, 5 specialized tools, autonomous replanning** |
| Innovation & Creativity | 20% | Procrastination AI learns your patterns; stress scoring; cascade detection |
| Google Technologies | 15% | AI Studio + Gemini 1.5 Pro + Cloud Run + function calling |
| Product Experience | 10% | Dark-themed SPA, real-time agent step visualization |
| Technical Implementation | 10% | 8 API endpoints, proper error handling, multi-step loop |
| Completeness | 5% | All features functional end-to-end |

---

## 👨‍💻 Author

**Satyam** — B.Tech CSE (2023–2027), ITER SOA University, Bhubaneswar
GitHub: [@Satyam5367](https://github.com/Satyam5367) | LeetCode: satyamsa122

---

*Built for BlockseBlock Hackathon · June 2026 · Powered by Google AI Studio*
