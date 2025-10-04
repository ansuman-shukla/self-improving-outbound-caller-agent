

# 🎙️ Voice Agent Evaluator & Automated Tuning Platform
<div align="center">

**An AI-powered platform for testing, evaluating, and automatically optimizing voice agent prompts for debt collection conversations**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini-2.5%20Flash-orange.svg)](https://ai.google.dev/)

[Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation)

</div>

# 📹 Demo Videos

Watch the project in action:

- [Demo Video 1](https://www.loom.com/share/ce19bf0f6d7940fb8cf51f7fe1411a8b?sid=28e25598-cd9c-49e0-8619-6b0da7dea8e2)
- [Demo Video 2](https://www.loom.com/share/168f8403fb5a4c50acfb9a24616c0ecd?sid=ba25d771-3901-4ef9-9d85-e2ff16187de3)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Star Features](#-star-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Technology Stack](#-technology-stack)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

The **Voice Agent Evaluator** is a sophisticated platform designed to systematically test, evaluate, and automatically improve voice agent system prompts for debt collection scenarios. Built with cutting-edge AI technology, it simulates realistic conversations, provides objective performance scoring, and uses AI-powered optimization to iteratively enhance agent behavior.

### What Problem Does It Solve?

**Traditional challenges in voice agent development:**
- ❌ Manual testing is slow, inconsistent, and biased
- ❌ No objective way to measure conversation quality
- ❌ Prompt engineering is trial-and-error based
- ❌ Difficult to test against diverse scenarios
- ❌ No systematic improvement methodology

**Our solution:**
- ✅ Automated conversation simulation with AI-powered debtors
- ✅ Objective, multi-dimensional scoring (Task Completion + Efficiency)
- ✅ AI-driven prompt optimization with Writer-Critique methodology
- ✅ Comprehensive scenario library with personality-based testing
- ✅ Complete audit trails and iteration tracking

---

## 🎯 Key Features

### 1. **The Library Hub** 📚
Central repository for managing conversational components:

- **Debtor Personalities**: 
  - Pre-built personality templates (Anxious, Aggressive, Cooperative, etc.)
  - Custom personality creation with detailed trait definitions
  - Personality-specific behavioral patterns and response styles
  
- **Agent Prompts**:
  - Version-controlled system prompts
  - Template library for different collection strategies
  - Prompt comparison and A/B testing capabilities

### 2. **Scenario Designer** 🎭
Intelligent scenario generation for realistic testing:

- **AI-Powered Generation**: 
  - Input a brief scenario description
  - Select debtor personality
  - AI generates complete backstory with financial details
  
- **Scenario Management**:
  - Editable scenarios with backstory customization
  - Scenario weighting for importance prioritization
  - Scenario categorization and tagging

### 3. **Manual Evaluation Engine** 🧪
Hands-on testing and analysis:

- **Conversation Simulation**:
  - Select any prompt + scenario combination
  - Real-time conversation generation (3-5 turns)
  - Natural dialogue flow with context awareness
  
- **Dual-Metric Scoring**:
  - **Task Completion** (0-100): Did agent achieve collection goals?
  - **Conversation Efficiency** (0-100): Was dialogue smooth and natural?
  - Detailed AI analysis explaining scores
  
- **Results Dashboard**:
  - Sortable/filterable evaluation history
  - Transcript viewer with speaker identification
  - Score comparison across prompts/scenarios

### 4. **Automated Tuning Loop** ⚡ (STAR FEATURE)
Self-improving AI optimization system:

- **Configuration**:
  - Select initial prompt
  - Set target performance score (0-100)
  - Choose test scenarios with importance weights (1-5)
  - Define max optimization iterations (1-10)
  
- **Iterative Optimization Process**:
  1. **Batch Testing**: Run prompt against all scenarios
  2. **Weighted Scoring**: Calculate aggregate performance
  3. **Failure Analysis**: AI examines low-scoring conversations
  4. **Prompt Improvement**: Writer agent generates enhanced prompt
  5. **Quality Control**: Critique agent validates improvements
  6. **Re-testing**: Evaluate new prompt
  7. Repeat until target reached or max iterations hit
  
- **Real-Time Monitoring**:
  - Live status updates (Pending → Running → Completed)
  - Progress indicators showing current iteration
  - Score progression tracking with improvement deltas
  - Iteration-by-iteration result breakdown
  
- **Results Analysis**:
  - Final optimized prompt with version tracking
  - Complete iteration history with scores
  - Evaluation transcripts for each iteration
  - Export-ready optimized prompts

### 5. **Outbound Caller Dashboard** 📞
Practical call management system:

- **Call Initiation**:
  - Country code selection (India, UK, US, Canada, Australia)
  - Debtor information input
  - Real-time call status tracking
  
- **Call History**:
  - Complete call records with timestamps
  - Status tracking (In Progress, Completed, Failed)
  - Transcript viewing and download

---

## ⭐ Star Features

### 🤖 **AI-Powered Self-Improvement**

The platform's **crown jewel** is its autonomous optimization capability:

**Writer-Critique Methodology:**
- **Writer Agent**: Analyzes failed conversations and generates improved prompts
- **Critique Agent**: Reviews proposals for quality and effectiveness
- **Iterative Refinement**: Up to 3 cycles of generation → critique → revision

**Why It's Revolutionary:**
- No human prompt engineering required during optimization
- Learns from actual conversation patterns and failures
- Generates contextually-aware improvements
- Built-in quality control prevents bad prompts

**Real-World Impact:**
```
Initial Prompt Score: 55/100 (Too aggressive, no empathy)
Iteration 1: 68/100 (Added empathy, better pacing)
Iteration 2: 81/100 (Balanced structure + flexibility)
Result: 47% improvement in 2 automated iterations
```

### 📊 **Weighted Multi-Scenario Testing**

Unlike simple A/B testing, our system:
- Tests against **multiple debtor personalities** simultaneously
- Assigns **importance weights** (1-5) to reflect real-world frequency
- Calculates **weighted averages** for holistic performance measurement
- Ensures prompts work across diverse situations, not just one

**Example Configuration:**
```
Scenario: Anxious First-Time Debtor (Weight: 5) → High priority
Scenario: Aggressive Non-Compliant (Weight: 3) → Medium priority  
Scenario: Cooperative Willing Payer (Weight: 2) → Low priority

Final score reflects realistic scenario distribution
```

### 🔄 **Complete Audit Trails**

Every optimization is fully traceable:
- All iterations recorded with timestamps
- Prompts versioned and stored
- Evaluation transcripts preserved
- Score progression tracked
- Enables reproducibility and debugging

### 🎨 **Modern, Intuitive UI**

Built with user experience in mind:
- Real-time updates without page refresh (polling every 3s)
- Responsive design for desktop and tablet
- Dark theme optimized for long sessions
- Expandable sections for detailed views
- Status indicators with color coding

---

## 🏗️ Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Library  │  │ Scenario │  │Evaluation│  │  Tuning  │   │
│  │   Hub    │  │ Designer │  │   Hub    │  │   Hub    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        │         REST API (FastAPI Backend)      │
        │                                          │
┌───────┼──────────────────────────────────────────┼──────────┐
│       ▼                                          ▼           │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Router    │  │   Services   │  │ Background      │   │
│  │  (FastAPI)  │  │   Layer      │  │ Tasks Queue     │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬────────┘   │
│         │                │                     │            │
│         ▼                ▼                     ▼            │
│  ┌──────────────────────────────────────────────────┐     │
│  │          Core Business Logic                      │     │
│  │  • Conversation Simulation                        │     │
│  │  • Evaluation Orchestration                       │     │
│  │  • Tuning Service (Writer-Critique)              │     │
│  │  • Transcript Analysis                            │     │
│  └──────────────────┬───────────────────────────────┘     │
└─────────────────────┼─────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼              ▼
   ┌────────┐   ┌─────────┐   ┌──────────┐
   │MongoDB │   │ Gemini  │   │ LiveKit  │
   │  DB    │   │   API   │   │   API    │
   └────────┘   └─────────┘   └──────────┘
    Persistence   AI Engine     Voice Calls
```

### Data Flow: Automated Tuning Loop

```
1. User Initiates Tuning
   └→ POST /api/tuning {prompt, scenarios, target}
        └→ Create TuningLoop document (PENDING)
             └→ Return tuning_loop_id immediately
                  └→ Launch BackgroundTask

2. Background Optimization Process
   ├→ Update status to RUNNING
   │
   ├→ FOR each iteration (1 to max_iterations):
   │   │
   │   ├→ Run Evaluations (parallel)
   │   │   ├→ Scenario A: Simulate conversation
   │   │   ├→ Scenario B: Simulate conversation  
   │   │   └→ Scenario C: Simulate conversation
   │   │
   │   ├→ Calculate Weighted Score
   │   │   └→ (scoreA×weightA + scoreB×weightB + scoreC×weightC) / (sum of weights)
   │   │
   │   ├→ Check Success
   │   │   └→ IF score >= target: BREAK (success!)
   │   │
   │   ├→ AI Improvement (Writer-Critique Cycle)
   │   │   ├→ Build context package (failures + transcripts)
   │   │   ├→ Writer: Generate improved prompt
   │   │   ├→ Critique: Review and validate
   │   │   └→ IF not approved: Writer revises (up to 3x)
   │   │
   │   ├→ Save New Prompt Version
   │   │   └→ Store in prompts collection with auto-generated name
   │   │
   │   └→ Record Iteration
   │       └→ Append to tuning_loop.iterations array
   │
   └→ Complete
       ├→ Update status to COMPLETED
       ├→ Set final_prompt_id
       └→ Record completion timestamp

3. Frontend Polling
   └→ GET /api/tuning/{id} every 3 seconds
        └→ Fetch updated status and results
             └→ Update UI with progress/scores
```

---

## 📁 Project Structure

```
outbound-caller-python/
│
├── backend/                          # FastAPI Backend
│   ├── main.py                       # Application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── .env.local                    # Environment variables
│   │
│   ├── api/                          # API Route Handlers
│   │   ├── router.py                 # Main API router
│   │   ├── personalities.py          # Personality CRUD endpoints
│   │   ├── prompts.py                # Prompt CRUD endpoints
│   │   ├── scenarios.py              # Scenario generation & CRUD
│   │   ├── evaluations.py            # Evaluation endpoints
│   │   └── tuning.py                 # Tuning loop endpoints
│   │
│   ├── models/                       # Pydantic Models
│   │   ├── personality.py            # Debtor personality models
│   │   ├── prompt.py                 # Agent prompt models
│   │   ├── scenario.py               # Test scenario models
│   │   ├── evaluation.py             # Evaluation result models
│   │   ├── tuning_loop.py            # Tuning loop models
│   │   └── call.py                   # Call management models
│   │
│   ├── services/                     # Business Logic Layer
│   │   ├── conversation_moderator.py # Conversation simulation engine
│   │   ├── transcript_evaluator.py   # AI-powered evaluation
│   │   ├── evaluation_orchestrator.py# Evaluation workflow manager
│   │   └── tuning_service.py         # Automated tuning logic
│   │
│   ├── core/                         # Core Infrastructure
│   │   ├── database.py               # MongoDB connection & operations
│   │   ├── gemini_client.py          # Gemini API wrapper
│   │   └── config/                   # Configuration files
│   │
│   ├── agents/                       # Agent Implementations
│   │   └── outbound_caller.py        # liveKit integration
│   │
│   └── test/                         # Unit & Integration Tests
│       ├── test_tuning_service.py
│       ├── test_evaluations_api.py
│       └── ...
│
├── frontend/                         # Next.js Frontend
│   ├── package.json                  # Node dependencies
│   ├── next.config.ts                # Next.js configuration
│   ├── tsconfig.json                 # TypeScript configuration
│   │
│   ├── src/
│   │   ├── app/                      # Next.js App Router
│   │   │   ├── page.tsx              # Outbound Caller Dashboard
│   │   │   ├── library/              # Library Hub page
│   │   │   ├── scenarios/            # Scenario Designer page
│   │   │   ├── evaluations/          # Evaluation Hub page
│   │   │   └── tuning/               # Tuning Hub pages
│   │   │       ├── page.tsx          # Tuning list view
│   │   │       └── [id]/page.tsx     # Tuning detail view
│   │   │
│   │   ├── components/               # React Components
│   │   │   ├── Sidebar.tsx           # Navigation sidebar
│   │   │   ├── PersonalityTable.tsx
│   │   │   ├── PromptTable.tsx
│   │   │   ├── ScenarioCard.tsx
│   │   │   ├── ManualEvaluationForm.tsx
│   │   │   ├── EvaluationResultsTable.tsx
│   │   │   ├── TuningInitiationForm.tsx
│   │   │   └── TuningRunsTable.tsx
│   │   │
│   │   ├── lib/                      # Utilities
│   │   │   └── api.ts                # API client functions
│   │   │
│   │   ├── types/                    # TypeScript Types
│   │   │   ├── library.ts
│   │   │   ├── scenario.ts
│   │   │   ├── evaluation.ts
│   │   │   └── tuning.ts
│   │   │
│   │   └── hooks/                    # Custom React Hooks
│   │       └── usePolling.ts         # Real-time update hook
│   │
│   └── public/                       # Static Assets
│
├── transcripts/                      # Generated Call Transcripts
├── KMS/logs/                         # Application Logs
│
├── README.md                         # This file
├── TODO.md                           # Project roadmap
├── prd.md                            # Product Requirements Document
└── PHASE_*_COMPLETE.md              # Implementation documentation
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104+ (Modern async Python web framework)
- **Language**: Python 3.11+
- **Database**: MongoDB 6.0+ (Document-based NoSQL)
- **AI Engine**: Google Gemini 2.5 Flash (Conversation generation & evaluation)
- **Voice API**: Twilio (Outbound calling)
- **Async Runtime**: asyncio + Motor (MongoDB async driver)

### Frontend
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript 5+
- **UI Library**: React 18+
- **Styling**: Tailwind CSS 3+
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Infrastructure
- **API Architecture**: RESTful with async background tasks
- **Real-time Updates**: Client-side polling (3s interval)
- **Data Validation**: Pydantic v2 (Backend), Zod-like validation (Frontend)
- **Code Quality**: ESLint, TypeScript strict mode

---

## 📋 Prerequisites

Before installation, ensure you have:

1. **Python 3.11 or higher**
   ```bash
   python --version  # Should show 3.11+
   ```

2. **Node.js 18+ and npm**
   ```bash
   node --version  # Should show 18+
   npm --version
   ```

3. **MongoDB 6.0+**
   - Local installation OR
   - MongoDB Atlas account (cloud option)

5. **Git** (for cloning the repository)

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/livekit-examples/outbound-caller-python.git
cd outbound-caller-python
```

### Step 2: Backend Setup

#### 2.1 Create Python Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 2.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2.3 Configure Environment Variables

Create `.env.local` file in the `backend/` directory:

```env
LIVEKIT_URL=LIVEKIT_URL
LIVEKIT_API_KEY=LIVEKIT_API_KEY
LIVEKIT_API_SECRET=LIVEKIT_API_SECRET
DEEPGRAM_API_KEY=DEEPGRAM_API_KEY
CARTESIA_API_KEY=your_Cartesia_API_Key
GOOGLE_API_KEY=GOOGLE_API_KEY
OPENAI_API_KEY=OPENAI_API_KEY
SIP_OUTBOUND_TRUNK_ID=SIP_OUTBOUND_TRUNK_ID
TRANSCRIPT_DIR=./transcripts
MONGODB_URI=MONGODB_URI
GEMINI_API_KEY=GEMINI_API_KEY
ELEVEN_API_KEY=ELEVEN_API_KEY
SARVAM_API_KEY=SARVAM_API_KEY
```

**Note**: Replace placeholder values with your actual API keys.

#### 2.4 Start MongoDB

If using local MongoDB:
```bash
# Windows (if installed as service):
net start MongoDB

# macOS:
brew services start mongodb-community

# Linux:
sudo systemctl start mongod
```

If using MongoDB Atlas, ensure your connection string is in `MONGODB_URI`.

#### 2.5 Initialize the Outbound Caller Agent ⚠️ **CRITICAL STEP**

**IMPORTANT**: You MUST run the outbound caller agent BEFORE starting the uvicorn server. If you start the server first, the voice calling agent will not work and will throw errors.

```bash
# Make sure you're in backend/ directory and venv is activated
cd backend
python .\agents\outbound_caller.py dev
```
This initializes the voice agent with LiveKit You should see output indicating the agent is registered. Once you see the success message, you can proceed to start the server
.

**Why this is required**: The outbound caller agent registers itself with the LiveKit service and sets up necessary webhooks. This registration must happen before the FastAPI server starts to ensure all endpoints are properly configured.

#### 2.6 Start Backend Server

After successfully running the outbound caller initialization:

```bash
# Make sure you're in backend/ directory and venv is activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs` (Swagger UI)

### Step 3: Frontend Setup

Open a **new terminal** window:

#### 3.1 Navigate to Frontend Directory

```bash
cd frontend  # From project root
```

#### 3.2 Install Node Dependencies

```bash
npm install
```

#### 3.3 Configure Environment Variables

Create `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 3.4 Start Development Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:3000`

### Step 4: Verify Installation

1. **Backend Health Check**:
   - Visit `http://localhost:8000/health`
   - Should return: `{"status": "healthy"}`

2. **Frontend Access**:
   - Visit `http://localhost:3000`
   - Should see the Outbound Caller Dashboard

3. **API Documentation**:
   - Visit `http://localhost:8000/docs`
   - Interactive Swagger UI for testing endpoints

---

## 📖 Usage Guide

### Quick Start Workflow

#### 1. Create Your First Personality

1. Navigate to **Library Hub** (`/library`)
2. Click **"Create Personality"**
3. Fill in details:
   ```
   Name: Anxious First-Timer
   Description: Nervous debtor making first late payment
   Core Traits: Anxious, Apologetic, Willing to Pay
   Behavioral Patterns: Speaks quickly, asks many questions, seeks reassurance
   ```
4. Click **"Create"**

#### 2. Create an Agent Prompt

1. In **Library Hub**, go to **Prompts** tab
2. Click **"Create Prompt"**
3. Enter prompt details:
   ```
   Name: Empathetic Collection Agent v1
   Prompt Text: 
   You are "Ana," a compassionate debt collection agent for SBI Bank...
   (Include full system instructions)
   
   Version: 1.0
   ```
4. Click **"Create"**

#### 3. Generate Test Scenarios

1. Navigate to **Scenario Designer** (`/scenarios`)
2. Click **"Generate New Scenario"**
3. Select personality: **Anxious First-Timer**
4. Enter brief: "Debtor lost job 2 months ago, has ₹15,000 credit card debt"
5. Click **"Generate"** - AI creates full backstory
6. Review and edit if needed
7. Click **"Save"**

Repeat for 2-3 more scenarios with different personalities.

#### 4. Run Manual Evaluation

1. Navigate to **Evaluation Hub** (`/evaluations`)
2. In **"Start New Evaluation"** form:
   - Select your prompt
   - Select a scenario
3. Click **"Run Evaluation"**
4. Wait ~30 seconds while:
   - AI simulates full conversation
   - Evaluator analyzes transcript
5. View results:
   - Task Completion Score
   - Conversation Efficiency Score
   - Detailed analysis
   - Full transcript

#### 5. Launch Automated Tuning Loop

1. Navigate to **Tuning Hub** (`/tuning`)
2. Click **"Start New Tuning Loop"**
3. Configure:
   ```
   Initial Prompt: Empathetic Collection Agent v1
   Target Score: 85
   Max Iterations: 5
   
   Scenarios:
   - Anxious First-Timer (Weight: 5)
   - Aggressive Non-Compliant (Weight: 3)
   - Cooperative Willing Payer (Weight: 2)
   ```
4. Click **"Start Tuning Loop"**
5. Monitor progress in real-time:
   - Status updates (Pending → Running → Completed)
   - Current iteration number
   - Score progression
6. Click on row to see detailed results
7. View final optimized prompt
8. Use optimized prompt in production

---

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Key Endpoints

#### Personalities
```http
GET    /personalities           # List all personalities
POST   /personalities           # Create new personality
GET    /personalities/{id}      # Get personality by ID
PUT    /personalities/{id}      # Update personality
DELETE /personalities/{id}      # Delete personality
```

#### Prompts
```http
GET    /prompts                 # List all prompts
POST   /prompts                 # Create new prompt
GET    /prompts/{id}            # Get prompt by ID
PUT    /prompts/{id}            # Update prompt
DELETE /prompts/{id}            # Delete prompt
```

#### Scenarios
```http
GET    /scenarios               # List all scenarios
POST   /scenarios/generate      # Generate scenario with AI
GET    /scenarios/{id}          # Get scenario by ID
PUT    /scenarios/{id}          # Update scenario
DELETE /scenarios/{id}          # Delete scenario
```

#### Evaluations
```http
POST   /evaluations             # Create evaluation (returns immediately)
GET    /evaluations             # List all evaluations
GET    /evaluations/{id}        # Get evaluation result (poll for completion)
DELETE /evaluations/{id}        # Delete evaluation
```

**Evaluation Request Body:**
```json
{
  "prompt_id": "507f1f77bcf86cd799439011",
  "scenario_id": "507f1f77bcf86cd799439012"
}
```

**Evaluation Response:**
```json
{
  "result_id": "507f1f77bcf86cd799439013",
  "status": "PENDING"  // Poll /evaluations/{result_id} for completion
}
```

#### Tuning Loops
```http
POST   /tuning                  # Start tuning loop (background task)
GET    /tuning                  # List all tuning loops
GET    /tuning/{id}             # Get tuning loop status & results (poll)
```

**Tuning Request Body:**
```json
{
  "initial_prompt_id": "507f1f77bcf86cd799439011",
  "target_score": 85,
  "max_iterations": 5,
  "scenarios": [
    {
      "scenario_id": "507f1f77bcf86cd799439012",
      "weight": 5
    },
    {
      "scenario_id": "507f1f77bcf86cd799439013",
      "weight": 3
    }
  ]
}
```

**Tuning Response (Immediate):**
```json
{
  "tuning_loop_id": "507f1f77bcf86cd799439014",
  "status": "PENDING",
  "current_iteration": null,
  "latest_score": null
}
```

**Tuning Status (Polling):**
```json
{
  "_id": "507f1f77bcf86cd799439014",
  "status": "RUNNING",
  "iterations": [
    {
      "iteration_number": 1,
      "prompt_id": "507f1f77bcf86cd799439015",
      "weighted_score": 72.5,
      "evaluation_ids": ["..."],
      "timestamp": "2025-10-04T16:20:00Z"
    }
  ],
  "config": { /* original config */ },
  "final_prompt_id": null,
  "created_at": "2025-10-04T16:15:00Z",
  "completed_at": null
}
```

### Interactive API Docs

Visit `http://localhost:8000/docs` for:
- Interactive API explorer
- Request/response schemas
- Try-it-out functionality
- Authentication testing

---

## ⚙️ Configuration

### Backend Configuration

**`backend/.env.local`**:
```env
# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=voice_agent_evaluator

# AI Services
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash  # Optional: default model

# LiveKit (for calls)
RETELL_API_KEY=your_key_here
RETELL_AGENT_ID=your_agent_id_here

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=True  # Auto-reload on code changes

# Rate Limiting
RATE_LIMIT_DELAY=8  # Seconds between Gemini API calls
```

### Frontend Configuration

**`frontend/.env.local`**:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### MongoDB Collections

The application creates these collections automatically:
- `personalities` - Debtor personality profiles
- `prompts` - Agent system prompts
- `scenarios` - Test scenarios
- `evaluations` - Evaluation results
- `tuning_loops` - Tuning loop records
- `calls` - Call records

---

## 👨‍💻 Development

### Running in Development Mode

**Backend (with auto-reload):**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (with hot-reload):**
```bash
cd frontend
npm run dev
```

### Code Style & Linting

**Backend (Python):**
```bash
# Install dev dependencies
pip install black flake8 mypy

# Format code
black backend/

# Lint
flake8 backend/

# Type checking
mypy backend/
```

**Frontend (TypeScript):**
```bash
# Lint
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix

# Type check
npm run type-check
```

### Adding New Features

1. **Backend API Endpoint**:
   - Add Pydantic models in `backend/models/`
   - Implement business logic in `backend/services/`
   - Create route handler in `backend/api/`
   - Add route to `backend/api/router.py`
   - Write tests in `backend/test/`

2. **Frontend Component**:
   - Create TypeScript types in `frontend/src/types/`
   - Add API functions in `frontend/src/lib/api.ts`
   - Build React component in `frontend/src/components/`
   - Create page in `frontend/src/app/`
   - Add navigation link in `Sidebar.tsx`

---

## 🧪 Testing

### Backend Unit Tests

```bash
cd backend
source venv/bin/activate

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test/test_tuning_service.py

# Run specific test
pytest test/test_tuning_service.py::test_calculate_weighted_average_basic
```

### Frontend Testing

```bash
cd frontend

# Install test dependencies
npm install --save-dev @testing-library/react @testing-library/jest-dom jest

# Run tests (if configured)
npm test
```

### Manual Testing Checklist

- [ ] Create personality
- [ ] Create prompt
- [ ] Generate scenario with AI
- [ ] Edit scenario backstory
- [ ] Run manual evaluation
- [ ] View evaluation results
- [ ] Start tuning loop
- [ ] Monitor tuning progress (watch status updates)
- [ ] View tuning details
- [ ] Check final prompt was created
- [ ] Verify prompt appears in Library

---

## 🚢 Deployment

### Production Considerations

1. **Environment Variables**:
   - Never commit `.env.local` files
   - Use environment-specific configs
   - Rotate API keys regularly

2. **Database**:
   - Use MongoDB Atlas for production
   - Enable authentication
   - Set up backups
   - Create indexes for performance

3. **Backend**:
   - Use production ASGI server (Gunicorn + Uvicorn workers)
   - Enable HTTPS
   - Set up rate limiting
   - Configure CORS properly
   - Add monitoring (logs, metrics)

4. **Frontend**:
   - Build for production: `npm run build`
   - Use CDN for static assets
   - Enable caching
   - Optimize images

### Docker Deployment (Optional)

Create `Dockerfile` for backend:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:6.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongodb:27017
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - mongodb
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

volumes:
  mongo_data:
```

Run with Docker:
```bash
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Voice calling agent throws errors when making calls ⚠️

**Symptoms**:
- Errors when trying to use the outbound calling functionality
- Agent registration failures

**Solution**:
```bash
# CRITICAL: You must run the outbound caller BEFORE starting the server
cd backend
# Ensure virtual environment is activated
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # macOS/Linux

# Run the outbound caller initialization
python .\agents\outbound_caller.py dev

# THEN start the server (in the same terminal or a new one with venv activated)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Why**: The outbound caller agent must register with LiveKit and set up webhooks before the FastAPI server starts. Running the server first will cause the calling functionality to fail.

#### 2. Backend won't start - "Port 8000 already in use"

**Solution**:
```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

#### 3. MongoDB connection error

**Solution**:
- Verify MongoDB is running: `mongosh` (should connect)
- Check `MONGODB_URI` in `.env.local`
- If using Atlas, verify IP whitelist
- Check network connectivity

#### 4. Gemini API rate limit errors

**Solution**:
- Increase `RATE_LIMIT_DELAY` in `.env.local` (default: 8 seconds)
- Check API quota in Google Cloud Console
- Verify API key is valid

#### 5. Frontend shows "Network error"

**Solution**:
- Verify backend is running: `curl http://localhost:8000/health`
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Check browser console for CORS errors
- Verify backend CORS configuration

#### 6. Tuning loop stays in PENDING forever

**Solution**:
- Check backend logs for errors
- Verify all required scenarios exist
- Ensure prompt ID is valid
- Check MongoDB for error messages in tuning_loop document

#### 7. Evaluation never completes

**Solution**:
- Check backend logs for Gemini API errors
- Verify prompt and scenario IDs are valid
- Check MongoDB for status (should be RUNNING → COMPLETED)
- Verify Gemini API key is working

### Debug Mode

**Enable verbose logging:**

Backend (`backend/main.py`):
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Frontend (browser console):
```javascript
localStorage.setItem('debug', 'true')
```

### Getting Help

1. Check existing [GitHub Issues](https://github.com/livekit-examples/outbound-caller-python/issues)
2. Review API documentation at `http://localhost:8000/docs`
3. Check MongoDB for data consistency
4. Enable debug logging and share relevant logs

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow existing code style
   - Add tests for new features
   - Update documentation
4. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add new evaluation metric"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request**

### Contribution Guidelines

- **Code Style**: Follow PEP 8 (Python), Airbnb style guide (JavaScript/TypeScript)
- **Testing**: All new features must include tests
- **Documentation**: Update README and inline docs
- **Commit Messages**: Use conventional commits format
  - `feat:` New feature
  - `fix:` Bug fix
  - `docs:` Documentation changes
  - `refactor:` Code refactoring
  - `test:` Test additions/changes

### Areas for Contribution

- 🐛 Bug fixes
- ✨ New features (evaluation metrics, UI improvements)
- 📚 Documentation improvements
- 🧪 Test coverage expansion
- 🌍 Internationalization
- ⚡ Performance optimizations

---

## 📄 License

This project is licensed under the MIT License. See `LICENSE` file for details.

---

## 🙏 Acknowledgments

- **LiveKit** - For the excellent voice agent framework
- **Google Gemini** - For powerful AI capabilities
- **FastAPI** - For the modern Python web framework
- **Next.js** - For the React framework
- **MongoDB** - For flexible data storage

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/livekit-examples/outbound-caller-python/issues)
- **Documentation**: [Wiki](https://github.com/livekit-examples/outbound-caller-python/wiki)
- **Email**: support@example.com (replace with actual contact)

---

<div align="center">

**Built with ❤️ for better voice agent development**

⭐ Star this repo if you find it helpful!

</div>
#



fix this readme structre for github pls 
