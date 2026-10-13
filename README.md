# ⚽ PitchLens AI — Premier League Broadcasting Copilot
### *Transforming Synthetic Football Data into Explainable Match Intelligence, Real-Time Narratives, and Broadcast Overlays*

[![Inside the Game Hackathon](https://img.shields.io/badge/Hackathon-Inside%20the%20Game-purple?style=for-the-badge&logo=microsoft)](https://aka.ms/insidethegame)
[![Microsoft Azure](https://img.shields.io/badge/Azure-AI%20Foundry%20%7C%20OpenAI-blue?style=for-the-badge&logo=microsoftazure)](https://azure.microsoft.com/)
[![Semantic Kernel](https://img.shields.io/badge/Agent%20Orchestration-Semantic%20Kernel%201.45-green?style=for-the-badge)](https://github.com/microsoft/semantic-kernel)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 🌟 Executive Summary & Elevator Pitch

Football is more than a final score. Every pass, shot, tackle, change in possession, and shift in pressure tells a deeper story. 

**PitchLens AI** is an end-to-end, AI-powered broadcasting copilot that ingests synthetic football-realistic event streams and transforms them into **explainable match intelligence**, **real-time multimodal narratives**, **automated studio recaps**, and **personalized audience experiences**. 

Whether serving a **data-hungry studio analyst**, a **casual fan on mobile**, or a **supporter tracking a favorite player**, PitchLens AI turns raw telemetry into meaningful storytelling and timed, machine-readable graphical overlays synchronized with the match.

---

## 🎯 Target Categories
- 🏆 **Grand Prize: Best Overall Solution** — Comprehensive end-to-end match intelligence and broadcasting experience.
- 💡 **Best Multi-Agent Orchestration** — Built with Semantic Kernel 1.45 and Azure AI Foundry.
- 🎨 **Best Azure Cloud Native Integration** — Event-driven microservices designed for Azure Container Apps & Cosmos DB.

---

## ⚡ The 5-Stage Pipeline (Direct Hackathon Brief Implementation)

PitchLens AI implements the exact **One pipeline with five stages** required by the official hackathon specification:

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐     ┌───────────────────┐     ┌────────────────────┐
│   (a) INGEST    │ ──> │  (b) INTERPRET   │ ──> │    (c) EXPLAIN    │ ──> │    (d) RENDER     │ ──> │  (e) PERSONALIZE   │
│                 │     │                  │     │                   │     │                   │     │                    │
│ Synthetic Match │     │ Advanced Stats & │     │ Why Moments Matter│     │ Synchronized Live │     │ Dual Audiences     │
│  Event Stream   │     │ Control vs Chaos │     │ Tactical Shifts   │     │ Graphic Overlays  │     │ & Multi-Language   │
└─────────────────┘     └──────────────────┘     └───────────────────┘     └───────────────────┘     └────────────────────┘
```

### Stage (a): Ingest (Synthetic Match Event Feed)
- Real-time ingestion of synthetic event streams: passes, shots, tackles, pressure, carries, recoveries, fouls, cards, and goals.
- Enriched with **physical speed metrics**:
  - `ball_speed_kmh` (e.g., 38–122 km/h dynamically calculated)
  - `shot_speed_kmh` (e.g., 85–125 km/h)
  - `player_speed_kmh` (sprint and movement tracking)
- **Pass Quality Telemetry**:
  - Exact Euclidean distance (`pass_distance_m` based on a 105m x 68m pitch)
  - Normalized `pass_difficulty_rating` (0.00 – 1.00 based on defensive density, pressure, and angle)
  - Outcome determination (complete, incomplete, intercepted).

### Stage (b): Interpret (Match Intelligence Engine)
- Aggregates event streams into high-level football states and metrics.
- Computes **Control vs. Chaos Index** (0–100):
  - Measures structural dominance vs. high-turnover transition volatility.
- Computes **Pitch Pressure Index** and identifies the **Dominant Pitch Zone**.
- Real-time running team statistics: Possession %, Total xG, Pass Accuracy %, Tackles Won, and Running Ball Velocity.

### Stage (c): Explain ("Why Moments Matter")
- Explains the strategic *why* behind critical inflection points rather than simply reporting raw events:
  - **Defensive Low-Block Breaches**: Explains half-space overloads, delayed midfield recoveries, and xG generation.
  - **Counter-Pressing Traps**: Analyzes turnover triggers that lead to high-probability transition chances.
  - **Line-Breaking Passes**: Identifies third-man vertical disruptions that eliminate defensive lines under high pressure.

### Stage (d): Render (Synchronized Broadcast Graphical Overlays)
- Generates timed, machine-readable graphical payloads for live match feeds, LED studio walls, and streaming overlays:
  - `LOWER_THIRD`: Goal speed & xG breakdown.
  - `SPEED_PASS_BADGE`: High-difficulty pass telemetry with velocity.
  - `MOMENTUM_GAUGE`: Control vs. Chaos transition warnings.
  - `PLAYER_SPOTLIGHT`: Real-time sprint velocity and distance covered.

### Stage (e): Personalize (Dual Audience & Multi-Language)
- Adapts the intelligence into **three distinct audience modes**:
  1. 🎙️ **Casual Fan Mode**: High-energy, emotional, accessible commentary designed for mainstream viewers.
  2. 📊 **Data-Hungry Analyst Mode**: Quantitative tactical telemetry with xG, ball velocities, pass difficulty %, and pitch coordinates.
  3. 🏃 **Player-Focused Mode**: Tracks any individual player's movements, sprints, heat positions, and distance covered throughout the 90 minutes.
- **Multi-Language Storytelling**: Instant native localized narratives in **English (EN)**, **Romanian (RO)**, and **Spanish (ES)**.

---

## 🛠️ Microsoft & Azure Technology Stack

| Technology | Role in PitchLens AI |
|:---|:---|
| **Microsoft Semantic Kernel (Python 1.45.0)** | Multi-agent orchestration, function calling, state routing, and tactical plugins |
| **Azure OpenAI Service / AI Foundry** | GPT-4o-mini deployment for real-time tactical reasoning, studio recaps, and Q&A |
| **Microsoft Foundry IQ Pattern** | Grounded knowledge retrieval connecting live match state to conversational responses without hallucinations |
| **Azure Container Apps (ACA)** | Serverless container hosting for the FastAPI backend and React frontend |
| **FastAPI & WebSockets** | High-throughput, real-time event streaming and REST API |
| **React 19 + TypeScript + Vite + Tailwind CSS** | Ultra-responsive 60fps broadcasting console with interactive pitch radar |

---

## 🚀 Quick Start Guide (Run Locally in 2 Minutes)

### Prerequisites
- **Python 3.11+** installed
- **Node.js 18+** and **npm** installed
- *(Optional)* Azure OpenAI API key (the application includes zero-latency intelligent fallbacks and works 100% out-of-the-box without keys).

### Option 1: One-Click Runner (PowerShell)
```powershell
# From the pitchlens-ai root directory
.\run_dev.ps1
```
This automatically starts both the Python backend on `http://localhost:8000` and the React frontend on `http://localhost:5173`.

---

### Option 2: Manual Setup

#### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*API Documentation is live at `http://localhost:8000/docs`.*

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Open `http://localhost:5173` in your browser.*

---

## 📡 API Endpoints

- `GET /api/match/teams` — Retrieve full synthetic squad rosters, attributes, and formations.
- `GET /api/match/state` — Retrieve current live match snapshot.
- `POST /api/match/focus-player` — Set the active player for Player-Focused Mode.
- `POST /api/match/language` — Switch real-time language (EN, RO, ES).
- `GET /api/match/recap` — Generate automated executive studio recap.
- `POST /api/match/ask` — Conversational AI Copilot grounded on live telemetry.
- `WS /ws/live` — High-speed real-time match simulation WebSocket stream.

---

## 🏆 Hackathon Evaluation Rubric Alignment

| Rubric Criterion | Weight | How PitchLens AI Excels |
|:---|:---:|:---|
| **1. Technological Implementation** | 20% | Clean, modular Python 3.12 architecture, strict Pydantic v2 schemas, typed TypeScript frontend, WebSocket streaming, and Docker support. |
| **2. Agentic Design & Innovation** | 20% | Semantic Kernel 1.45 orchestration across 5 distinct pipeline stages with multi-agent handoffs and grounded reasoning. |
| **3. Real-World Impact & Applicability** | 20% | Directly addresses the multi-billion dollar football broadcasting and streaming industry (Sky Sports, Premier League Productions, Amazon Prime). |
| **4. User Experience & Presentation** | 20% | Professional Premier League broadcast aesthetic, interactive pitch visualizer, synchronized graphic overlays, and persona switchers. |
| **5. Adherence to Category** | 20% | Uses 100% synthetic realistic data, incorporates all requested speed/pass difficulty metrics, and delivers multi-language personalization. |

---

## 👥 Team & Submission Info
- **Project**: PitchLens AI
- **Hackathon**: Inside the Game: Developer Hackathon (Microsoft & Premier League)
- **Submission Date**: October 2026
