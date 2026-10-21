# ⚽ PitchLens AI — Premier League Broadcasting Copilot
### *Transforming Synthetic Football Data into Explainable Match Intelligence, Real-Time Multimodal Narratives, and Broadcast Overlays*

[![Inside the Game Hackathon](https://img.shields.io/badge/Hackathon-Inside%20the%20Game-purple?style=for-the-badge&logo=microsoft)](https://aka.ms/insidethegame)
[![Microsoft Azure](https://img.shields.io/badge/Azure-AI%20Foundry%20%7C%20OpenAI-blue?style=for-the-badge&logo=microsoftazure)](https://azure.microsoft.com/)
[![Semantic Kernel](https://img.shields.io/badge/Agent%20Orchestration-Semantic%20Kernel%201.45-green?style=for-the-badge)](https://github.com/microsoft/semantic-kernel)
[![Microsoft Cognitive Speech](https://img.shields.io/badge/Neural%20Audio-Cognitive%20TTS%20HD-orange?style=for-the-badge&logo=microsoft)](https://azure.microsoft.com/products/ai-services/text-to-speech)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 🌟 Executive Summary & Elevator Pitch

Football is far more than a final scoreline. Every line-breaking pass, counter-pressing turnover, high-xG chance, tactical foul, and set-piece routine tells a deeper tactical story.

**PitchLens AI** is an end-to-end, enterprise-grade AI broadcasting copilot designed for the **Microsoft & Premier League "Inside the Game: Developer Hackathon"**. It ingests synthetic football-realistic event streams and elevates them into:
1. **Explainable Match Intelligence** — Unravels *why* key moments happen (space creation, third-man runs, defensive low blocks, counter-pressing traps).
2. **Synchronized Multimodal Narratives** — Delivers real-time textual and **Neural Audio Commentary** in multiple languages (English, Romanian, Spanish) powered by Microsoft Cognitive Neural Speech.
3. **Calibrated Set-Piece Routines & Tactical Holograms** — Simulates realistic corners, penalties (11m spot with 20 players cleared), free kicks (9.15m defensive wall), fouls, and animated 3D yellow/red cards with on-pitch turf reticles.
4. **Official Opta-Calibrated Match Statistics** — Live tracking of Expected Goals (xG), Possession %, Total Shots, Shots on Target, Corners, Fouls, Yellow/Red Cards, and Pass Accuracy.
5. **League-Wide Championship Hub** — A dedicated Premier League overview featuring the "As It Stands" live standings table, Title Race Tracker, and Season Individual Honors (Golden Boot, Playmaker Award, Golden Glove).

---

## 🎯 Target Hackathon Categories
- 🏆 **Grand Prize: Best Overall Solution** — Comprehensive end-to-end broadcasting copilot spanning physics ingestion, tactical explainability, live TV overlays, neural voice commentary, and multi-game league management.
- 💡 **Best Multi-Agent Orchestration** — Built with Microsoft Semantic Kernel (Python 1.45) orchestrating five distinct pipeline stages with grounded reasoning and memory handoffs.
- 🎨 **Best Azure Cloud Native Integration** — Event-driven microservices designed for Azure Container Apps (ACA), Azure AI Foundry, and Microsoft Cognitive Speech Services.

---

## ⚡ The 5-Stage Pipeline (Direct Hackathon Brief Implementation)

PitchLens AI implements the exact **One pipeline with five stages** required by the official hackathon specification:

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐     ┌───────────────────┐     ┌────────────────────┐
│   (a) INGEST    │ ──> │  (b) INTERPRET   │ ──> │    (c) EXPLAIN    │ ──> │    (d) RENDER     │ ──> │  (e) PERSONALIZE   │
│                 │     │                  │     │                   │     │                   │     │                    │
│ Synthetic Match │     │ Advanced Stats & │     │ Why Moments Matter│     │ Synchronized Live │     │ Dual Audiences,    │
│  Event Stream   │     │ Control vs Chaos │     │ Tactical Shifts   │     │ Graphic Overlays  │     │ Neural Voice & RO  │
└─────────────────┘     └──────────────────┘     └───────────────────┘     └───────────────────┘     └────────────────────┘
```

### Stage (a): Ingest (Synthetic Match Event Feed & Physics)
- Real-time ingestion of synthetic event streams across 22 players: passes, shots, tackles, interceptions, carries, recoveries, fouls, yellow/red cards, corners, penalties, and goals.
- **Physical Speed & Telemetry Metrics**:
  - `ball_speed_kmh` (38–124 km/h dynamically calculated based on pass type or shot velocity).
  - `shot_speed_kmh` (up to 124 km/h for penalties and long-range rockets).
  - `player_speed_kmh` (individual sprint and recovery speed tracking).
- **Pass Quality Telemetry**:
  - Exact Euclidean distance (`pass_distance_m` based on a 105m x 68m pitch).
  - Normalized `pass_difficulty_rating` (0.00 – 1.00 based on defensive density, interceptor angles, and pressing intensity).
  - Outcome determination (complete, incomplete, intercepted, out of bounds).

### Stage (b): Interpret (Match Intelligence & Official Opta Stats)
- Aggregates event streams into high-level tactical states and metrics.
- Computes **Control vs. Chaos Index** (0–100):
  - Quantifies structural possession dominance vs. frantic high-turnover transition volatility.
- Computes **Pitch Pressure Index** and identifies the **Dominant Pitch Zone** (e.g., *Attacking Third*, *Midfield Battleground*, *Defensive Low Block*).
- **Official Premier League & Opta-Calibrated Match Statistics**:
  - Expected Goals (xG cumulative tracking).
  - Possession % based on active possession time and chain lengths.
  - Total Shots & Shots on Target.
  - Corner Kicks.
  - Fouls Committed.
  - Yellow Cards (`🟨`) & Red Cards (`🟥`).
  - Pass Accuracy %.

### Stage (c): Explain ("Why Moments Matter")
- Explains the strategic *why* behind critical inflection points rather than simply reporting raw events:
  - **Defensive Low-Block Breaches**: Explains half-space overloads, delayed midfield recoveries, and xG creation.
  - **Counter-Pressing Traps**: Analyzes turnover triggers leading to high-probability transition windows within 8 seconds.
  - **Line-Breaking Passes**: Identifies third-man vertical disruptions that bypass opposition pressing waves.
  - **Disciplinary Sanctions**: Analyzes tactical fouls that interrupt goalscoring opportunities and details the defensive tactical cost of yellow/red cards.

### Stage (d): Render (Synchronized Broadcast Graphical Overlays)
- Generates timed, machine-readable graphical payloads for live feeds, LED studio walls, and TV broadcasts:
  - `LOWER_THIRD`: Goal speed & xG breakdown, Penalty conversion drama, Red Card dismissals.
  - `SPEED_PASS_BADGE`: High-difficulty pass telemetry with ball velocity and distance.
  - `MOMENTUM_GAUGE`: Control vs. Chaos transition warnings and chaos phases.
  - `PLAYER_SPOTLIGHT`: Real-time sprint speed, ground covered, and player heat position.
  - **On-Turf Holographic Reticles**: Concentric pulsing corner arc beacon (`🚩 CORNER FLAG`), penalty spot targeting reticle (`🎯 11m PENALTY SPOT`), foul markers (`⚠️ FOUL SPOT`), and disciplinary card badges (`🟨 BOOKED` / `🟥 SENT OFF`).

### Stage (e): Personalize (Multi-Persona & Microsoft Neural Audio)
- Adapts match intelligence into **three distinct audience modes**:
  1. 🎙️ **Casual Fan Mode**: High-energy, emotional, accessible commentary designed for mainstream viewers.
  2. 📊 **Data-Hungry Analyst Mode**: Quantitative tactical telemetry with xG, ball velocities, pass difficulty %, and pitch coordinates.
  3. 🏃 **Player-Focused Mode**: Tracks any individual player's movements, sprints, heat positions, and distance covered throughout the 90 minutes.
- **Multilingual Neural Voice Streaming**:
  - **English (EN)**: `en-GB-RyanNeural` (Authentic British Premier League broadcast voice).
  - **Romanian (RO)**: `ro-RO-EmilNeural` (Natural, high-fidelity Romanian commentary).
  - **Spanish (ES)**: `es-ES-AlvaroNeural` (Passionate Spanish commentary).
  - Instant live synchronization: switching language immediately re-generates and speaks the commentary in the selected language.

---

## 🏟️ Advanced Set-Piece & Disciplinary Simulation

PitchLens AI features an advanced set-piece state machine that replicates real Premier League tactical routines:

| Set Piece / Event | Tactical Setup & Coordinates | On-Pitch & TV Visuals |
|:---|:---|:---|
| **Corner Kick** | Ball & taker placed at corner flag `(99.5, 1.0)` or `(99.5, 99.0)`. Goal corridors packed with aerial threats. Defending GK anchored in 6-yard corridor. | Pulsing cyan corner arc beacon + `🚩 CORNER FLAG` label. Floating `🚩 Corner Taker` badge with cyan halo ring. Curling cross trajectory at 82 km/h. |
| **Penalty Kick** | Ball on the 11m spot `(88.5, 50.0)`. Taker 2.5m behind. GK on the goal line. **All other 20 players cleared outside the 18-yard box**. | Holographic magenta/gold target reticle on the turf + `🎯 11m PENALTY SPOT`. Floating `🎯 Penalty Taker` badge with electric magenta halo. TV banner: `💥 PENALTY KICK • xG 0.79`. |
| **Direct Free Kick** | Ball placed at 24m danger zone. **4-man defensive wall organized at regulation 9.15m distance**. | Golden ball trajectory curling over the wall at ~100 km/h. TV overlay: `🎯 DIRECT FREE KICK (24m)`. |
| **Tactical Foul** | Whistle blown at exact point of infraction `(x, y)`. Attacking team retains possession. | Amber pulsing warning ripple + `⚠️ FOUL SPOT` turf label. Offender badge: `⚠️ Foul`. Victim badge: `🩹 Fouled`. Top banner: `⚠️ REFEREE FOUL WHISTLE`. |
| **Yellow / Red Card** | Brandished on cynical or second-yellow challenges. Player card counters and team stats incremented. | Animated 3D floating badge: `🟨 YELLOW CARD` or `🟥 RED CARD`. Pulsing yellow/red halo ring around player. Turf badge: `🟨 BOOKED` / `🟥 SENT OFF`. |

---

## 🏆 Premier League Championship Hub & Standings

Beyond the single-match broadcast view, PitchLens AI provides an all-encompassing **Standings & Hub** tab:

1. **Live "As It Stands" Standings Table**:
   - Dynamic 20-club league table updated in real-time as goals occur across the concurrent fixtures.
   - Rank shift indicators with animated climb/drop arrows (▲ / ▼ / —).
   - Visual qualification zones: **UEFA Champions League** (1–4, blue accent), **UEFA Europa League** (5, amber accent), and **Relegation Drop Zone** (18–20, red accent).
   - Click any match in the table to instantly switch camera and broadcast to that match!
2. **Title Race Live Tracker**:
   - Compares the top 3 contenders dynamically (e.g. *Arsenal, Man City, Liverpool*).
   - Displays live points margin to 1st place (`LEADER`, `-1 PTS`, etc.), goal difference, and matches played.
3. **Official Season Individual Leaders**:
   - ⚽ **Golden Boot (Top Scorers)**: Erling Haaland (21), Mohamed Salah (18), Ollie Watkins (16), Cole Palmer (15), Bukayo Saka (14).
   - 🅰️ **Playmaker Award (Most Assists)**: Kevin De Bruyne (12), Mohamed Salah (10), Bukayo Saka (10), Cole Palmer (9), Martin Ødegaard (8).
   - 🧤 **Golden Glove (Clean Sheets)**: David Raya (13), Ederson (11), Alisson Becker (10), Emiliano Martínez (9), Guglielmo Vicario (8).
4. **Relegation Scrap (Bottom 3)**:
   - Compares 17th position (safety threshold) against positions 18, 19, 20 with the exact points needed to escape the drop.
5. **Matchweek 28 League Pulse**:
   - Aggregated goals scored across all 10 fixtures, goals-per-match average, and concurrent active live games.

---

## 🛠️ Microsoft & Azure Technology Stack

| Technology | Role in PitchLens AI |
|:---|:---|
| **Microsoft Semantic Kernel (Python 1.45.0)** | Multi-agent pipeline orchestration, tactical reasoning plugins, and state routing |
| **Azure OpenAI Service / AI Foundry** | GPT-4o-mini deployment for real-time tactical reasoning, executive studio recaps, and interactive fan Q&A |
| **Microsoft Cognitive Speech Services (TTS)** | High-fidelity neural voice synthesis streaming real-time broadcast commentary (`ro-RO-EmilNeural`, `en-GB-RyanNeural`, `es-ES-AlvaroNeural`) |
| **Microsoft Foundry Grounded IQ Pattern** | Grounded knowledge retrieval connecting live match state directly to conversational responses without hallucinations |
| **FastAPI & WebSockets** | High-throughput asynchronous event streaming, REST API, and sub-50ms tick dispatch |
| **React 19 + TypeScript + Vite + Tailwind CSS** | 60fps broadcasting console, interactive SVG pitch, smooth GPU player animations, and Premier League broadcast graphics |

---

## 🎬 3-Minute Hackathon Demo Script (Guide for Judges)

If presenting PitchLens AI during a live demo or video walkthrough, follow this 3-step sequence:

```
[0:00 - 1:00] THE BROADCAST STUDIO & TACTICAL INTELLIGENCE
1. Open http://localhost:5173. Show the side-by-side pitch and commentary layout.
2. Point out the smooth 22-player movement, goalkeeper goalmouth anchoring, and ball velocity badges.
3. Turn on Audio (speaker icon in navbar) to hear the natural Microsoft Neural Voice commentary.
4. Switch language from EN to RO — show how the commentary instantly switches to Romanian with natural neural inflection.

[1:00 - 2:00] SET PIECES & EXPLAINABILITY
5. Watch or trigger a Corner Kick: point out the ball at the corner quadrant, the pulsing arc, and the floating "Corner Taker" badge.
6. Watch or trigger a Penalty Kick: show the 11m reticle, the 20 outfield players cleared outside the 18-yard box, and the 1v1 duel.
7. Show the Disciplinary Cards: 3D floating yellow/red card above the penalized player with the animated halo ring.
8. Point out the Official Match Statistics panel (xG, Total Shots, Corners, Fouls, Yellow/Red Cards).

[2:00 - 3:00] PERSONALIZATION & CHAMPIONSHIP HUB
9. Switch personas: click "Casual Fan" (emotional commentary), then "Data Analyst" (xG and telemetry).
10. Click any player on the pitch: show Player Focus Mode with individual sprint speed, distance covered, and live heatmap.
11. Click "Standings & Hub" in the navbar: showcase the 20-team live table, the Title Race Tracker, and the Season Leaders (Golden Boot, Assists, Clean Sheets).
12. Click "Ask PitchLens AI" (bottom-right chat) or "Studio Recap" to show grounded Azure OpenAI responses.
```

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
- `GET /api/match/clubs` — Retrieve list of all 20 Premier League clubs with badges and metadata.
- `GET /api/match/state` — Retrieve current live match snapshot.
- `POST /api/match/switch-fixture` — Switch camera to any of the 10 concurrent matchweek fixtures.
- `POST /api/match/focus-player` — Set the active player for Player-Focused Mode.
- `POST /api/match/language` — Switch real-time language (EN, RO, ES).
- `GET /api/audio/tts?text=...&lang=...` — Stream high-fidelity Microsoft Cognitive Neural Audio commentary.
- `GET /api/match/recap` — Generate automated executive studio recap.
- `POST /api/match/ask` — Conversational AI Copilot grounded on live telemetry.
- `WS /ws/live` — High-speed real-time match simulation WebSocket stream.

---

## 🏆 Hackathon Evaluation Rubric Alignment

| Rubric Criterion | Weight | How PitchLens AI Excels |
|:---|:---:|:---|
| **1. Technological Implementation** | 20% | Modular Python 3.12 architecture, strict Pydantic v2 models, typed TypeScript React 19 frontend, WebSocket event bus, and zero-error production builds. |
| **2. Agentic Design & Innovation** | 20% | Semantic Kernel 1.45 multi-agent pipeline spanning Ingestion, Interpretation, Tactical Explainability, Overlays, and Neural Speech. |
| **3. Real-World Impact & Applicability** | 20% | Directly addresses the multi-billion dollar football broadcasting and streaming industry (Sky Sports, Premier League Productions, Amazon Prime). |
| **4. User Experience & Presentation** | 20% | Authentic Premier League broadcast aesthetic, 60fps 2D pitch, synchronized graphic overlays, persona switchers, and comprehensive Championship Hub. |
| **5. Adherence to Category** | 20% | Uses 100% synthetic realistic football event feeds, incorporates all requested physical speed/pass difficulty metrics, and delivers multi-language neural personalization. |

---

## 👥 Team & Submission Info
- **Project**: PitchLens AI
- **Hackathon**: Inside the Game: Developer Hackathon (Microsoft & Premier League)
- **Submission Date**: October 2026
