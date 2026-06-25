# Deadline Guardian — Project Description
## BlockseBlock Hackathon · June 2026

---

## Problem Statement Selected
**The Last-Minute Life Saver**

---

## Solution Overview

Deadline Guardian is an autonomous AI productivity agent — not a reminder app, but a genuine
multi-step AI system that thinks, acts, observes, and replans. It is built on Gemini 1.5 Pro
function calling, enabling a real agentic loop: the system calls specialized tools, observes
results, and reasons across multiple steps before producing a concrete action plan.

The core breakthrough is autonomous conflict detection: when any new task is added, the agent
immediately re-evaluates ALL existing tasks, runs cascade analysis to find which deadlines will
collide, and proposes a revised priority order — without the user asking. This is what separates
Deadline Guardian from every other productivity tool.

Live App: [YOUR_DEPLOYED_URL]
GitHub: [YOUR_GITHUB_URL]

---

## Key Features

1. Multi-Step AI Agent (Gemini 1.5 Pro Function Calling)
   - Real agent loop: Think → Call Tool → Observe → Think again → Conclude
   - 5 specialized tools: analyze_deadline_risk, detect_conflict_cascade,
     compute_procrastination_pattern, generate_rescue_plan, generate_micro_plan
   - Agent runs 3–6 iterations per request, not a single API call
   - Judges can WATCH the agent reasoning in real-time on the "AI Agent" screen

2. Autonomous Conflict Cascade Detection
   - When a task is added, agent auto-detects which other deadlines will cascade
   - Calculates total overcommitment hours and identifies the trigger task
   - Proposes specific actions: reschedule/deprioritize/delegate/drop

3. Procrastination AI — Personalized Pattern Learning
   - Analyzes task completion history to find delay patterns by category
   - Computes a 0–100 procrastination score that feeds into risk calculations
   - Identifies worst/best categories and gives a behavior-change recommendation
   - This is completely unique — no other hackathon entry has this

4. AI Task Prioritization with Procrastination Adjustment
   - Ranks tasks by urgency + impact + personal procrastination score
   - Returns start-by time, survival probability, and one specific next action
   - Urgency = Critical / High / Medium / Low based on real deadline math

5. Energy-Aware Daily Scheduler
   - Generates an hourly plan aligned to user's peak energy window
   - Schedules cognitively demanding tasks at high-energy periods
   - Includes mandatory breaks, meals, buffer time

6. Task Breakdown Engine
   - Splits any task into 20–40 min subtasks typed as thinking/doing/reviewing
   - Each subtask includes duration, type, and a specific productivity tip

7. Smart Context-Aware Reminders
   - Personalized nudge messages (not generic alerts)
   - Urgency-matched: critical (<3h), high (<12h), normal
   - One specific actionable next step per reminder

8. AI Workload Coach
   - Daily situation-aware motivational message based on actual task state
   - Mood: motivating / warning / celebrating / urgent

9. Google Calendar Integration
   - Detects conflicts between calendar meetings and task deadlines
   - Suggests which tasks to reschedule when meetings eat available time

10. Voice Input with NLP Parsing
    - Web Speech API captures voice → Gemini parses into structured task
    - Extracts: task name, deadline, category, estimated hours

11. Habit Tracker with Streak Tracking
    - 7-day visual grid per habit
    - Automatic streak calculation

---

## Technologies Used

AI / Machine Learning:
- Gemini 1.5 Pro — function calling, multi-step reasoning, NLP parsing
- Procrastination pattern analysis (statistical + AI hybrid)
- Context-aware natural language generation

Backend:
- Python 3.11
- Flask 3.0 (REST API)
- Gunicorn (production WSGI server)

Frontend:
- HTML5 / CSS3 / Vanilla JavaScript
- Single-page application (SPA)
- Web Speech API (voice input)
- localStorage (client-side state persistence)

Deployment:
- Docker (containerization)
- Google Cloud Run (serverless)

---

## Google Technologies Utilized

| Technology | How Used |
|-----------|----------|
| Google AI Studio | Primary build and deployment platform |
| Gemini 1.5 Pro API | Multi-step agent loop, function calling, all AI features |
| google-generativeai Python SDK | Backend API integration |
| Google Cloud Run | Serverless container deployment (via AI Studio deploy) |
| Gemini Function Calling | 5 specialized tools called autonomously by the agent |

---

## Agentic Architecture

User adds task or makes request
          ↓
DeadlineGuardianAgent.run() starts
          ↓
Gemini 1.5 Pro receives context + task list
          ↓
Gemini decides to call: analyze_deadline_risk
          ↓ (tool result fed back)
Gemini decides to call: detect_conflict_cascade
          ↓ (tool result fed back)
Gemini decides to call: compute_procrastination_pattern
          ↓ (tool result fed back)
If crisis: Gemini calls generate_rescue_plan
          ↓
Gemini synthesizes ALL tool results → Final action plan
          ↓
Frontend displays step-by-step reasoning to user

This is a real autonomous loop — not a scripted chain.
The agent decides WHICH tools to call based on what it discovers.

---

## What Makes This Rank 1

Most hackathon entries:
- Call Gemini once → get a response → show it
- That is a chatbot, not an agent

Deadline Guardian:
- Runs a LOOP where Gemini calls tools, gets real data, reasons across results
- The agent decides autonomously what to investigate next
- Has a proprietary procrastination scoring system no other team built
- Visualizes the agent's reasoning process live (judges can SEE it thinking)
- Calendar integration adds Google tech depth for the 15% score

---

*Submitted by: Satyam | B.Tech CSE, ITER SOA University*
*GitHub: Satyam5367 | LeetCode: satyamsa122*
*Hackathon: BlockseBlock, June 2026*
