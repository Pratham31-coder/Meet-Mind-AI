# 🧠 MeetMind AI

### Turn hours of meeting recordings into searchable, actionable knowledge.

MeetMind AI is an **AI-powered meeting intelligence platform** that transforms YouTube videos and local meeting recordings into structured, searchable, and conversational knowledge.

Instead of manually watching an hour-long meeting to find **what was discussed, what decisions were made, who needs to do what, or what questions remain unanswered**, MeetMind processes the recording and produces a complete meeting knowledge base in minutes.

It combines **GPU-accelerated speech recognition, multilingual transcription, LLM-powered information extraction, vector search, and Retrieval-Augmented Generation (RAG)** into a single application.

---

## 🎯 The Problem

Meetings contain a huge amount of valuable information, but that information is usually trapped inside long audio/video recordings.

After a meeting, people often have to:

- Rewatch recordings to find important discussions
- Manually write meeting summaries
- Search through transcripts for specific information
- Remember who was assigned which task
- Identify decisions made during discussions
- Follow up on unanswered questions
- Spend time listening to an entire recording just to find one detail

**MeetMind AI solves this by turning an unstructured recording into an interactive knowledge base.**

Instead of asking:

> *"Where in the 60-minute meeting did they discuss the deployment deadline?"*

You can simply ask:

> **"What was the final deployment deadline?"**

And MeetMind retrieves the relevant context and generates the answer.

---

# ✨ What MeetMind AI Does

### 🎥 1. Ingest Meeting Content

MeetMind accepts:

- YouTube video URLs
- Local audio files
- Local video files
- Meeting recordings

The audio is automatically extracted and converted into a consistent format using **FFmpeg**.

---

### ⚡ 2. GPU-Accelerated Transcription

For English meetings, MeetMind runs **OpenAI Whisper locally using PyTorch CUDA**, allowing transcription to utilize an NVIDIA GPU instead of relying entirely on CPU processing.

For Hinglish conversations, MeetMind integrates **Sarvam Speech-to-Text** to generate an English transcript from Indian-language speech.

This makes the system suitable for real-world meetings where participants may naturally switch between English and Indian languages.

**Transcription pipeline:**

```text
Meeting Recording
       ↓
Audio Extraction
       ↓
16 kHz Mono WAV
       ↓
Whisper / Sarvam
       ↓
Clean Transcript
```

---

### 🧠 3. AI-Powered Meeting Intelligence

The transcript is processed using **Groq's high-speed LLM inference**.

MeetMind automatically extracts:

- 📌 Meeting title
- 📝 Comprehensive summary
- ✅ Action items
- 👤 Task assignees
- 📅 Deadlines
- 🎯 Key decisions
- ❓ Open questions

Instead of receiving a raw transcript containing thousands of words, users get information organized around what actually matters.

Example:

```text
ACTION ITEMS

1. Pratham
   → Complete API integration
   → Deadline: Friday

2. Rahul
   → Prepare deployment documentation
   → Deadline: Monday
```

---

# 💬 4. Chat With Your Meeting

This is where MeetMind goes beyond traditional transcription tools.

The transcript is chunked, embedded, and stored in a **ChromaDB vector database**.

Users can then ask natural-language questions about the meeting.

For example:

```text
User:
"What problems did the team identify with the current API?"

MeetMind:
"The team identified three major issues..."
```

Other possible queries:

```text
"Who was responsible for the database migration?"

"What decisions were made regarding deployment?"

"What concerns did the team raise about the timeline?"

"Did anyone mention a problem with authentication?"

"What are the unresolved questions?"

"Summarize everything discussed about the frontend."
```

The system retrieves the most relevant transcript chunks before generating the answer.

### RAG Pipeline

```text
User Question
      ↓
Embedding
      ↓
ChromaDB Similarity Search
      ↓
Relevant Transcript Chunks
      ↓
Groq LLM
      ↓
Context-Aware Answer
```

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │  YouTube / Local    │
                         │   Audio / Video     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   FFmpeg / yt-dlp   │
                         │   Audio Processing  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                     ┌────────────────────────────┐
                     │    Speech Recognition      │
                     │                            │
                     │ Whisper + CUDA   Sarvam    │
                     │    English       Hinglish  │
                     └──────────────┬─────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      Transcript     │
                         └──────────┬──────────┘
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
          ┌───────────────────┐          ┌────────────────────┐
          │    Groq LLM       │          │ HuggingFace        │
          │                   │          │ Embeddings         │
          │ Summary           │          └─────────┬──────────┘
          │ Action Items      │                    │
          │ Decisions         │                    ▼
          │ Questions         │          ┌────────────────────┐
          └───────────────────┘          │     ChromaDB       │
                                         │  Vector Knowledge  │
                                         │       Base         │
                                         └─────────┬──────────┘
                                                   │
                                                   ▼
                                         ┌────────────────────┐
                                         │   RAG Engine        │
                                         │   LangChain         │
                                         └─────────┬──────────┘
                                                   │
                                                   ▼
                                         ┌────────────────────┐
                                         │    Groq LLM         │
                                         │ Contextual Answer   │
                                         └────────────────────┘
```

---

# 🚀 Why This Project Is Different

MeetMind is not simply a **speech-to-text application**.

It combines several AI systems into one end-to-end pipeline:

| Capability | Technology |
|---|---|
| Video acquisition | yt-dlp |
| Audio processing | FFmpeg |
| Speech recognition | OpenAI Whisper |
| GPU acceleration | PyTorch + CUDA |
| Hinglish transcription | Sarvam AI |
| LLM inference | Groq |
| Structured extraction | LLM + structured prompting |
| Embeddings | HuggingFace |
| Vector database | ChromaDB |
| RAG | LangChain |
| Backend | FastAPI |
| Frontend | React + Vite |
| Database | SQLAlchemy |

The result is an end-to-end AI system rather than an isolated ML model or simple chatbot.

---

# 🧩 Technical Highlights

### Local GPU Inference

Whisper transcription and embedding generation can run locally on an NVIDIA GPU using CUDA.

```text
CPU-only processing
        ↓
        ❌ slower transcription / embeddings

NVIDIA CUDA
        ↓
        ⚡ hardware-accelerated inference
```

This also keeps the core transcription workload local rather than sending every recording directly to a cloud transcription service.

---

### Per-Meeting Knowledge Bases

Each meeting gets its own vector database.

```text
Meeting A
 └── ChromaDB
      └── Meeting-specific embeddings

Meeting B
 └── ChromaDB
      └── Meeting-specific embeddings
```

This prevents unrelated meetings from contaminating retrieval results and keeps conversations grounded in the selected meeting.

---

### RAG Instead of Sending the Entire Transcript

Rather than passing an entire long transcript to the LLM for every question, MeetMind:

1. Splits the transcript into chunks
2. Generates embeddings
3. Stores them in ChromaDB
4. Retrieves the most relevant chunks
5. Sends only relevant context to the LLM
6. Generates the final answer

This makes long-meeting conversations much more practical.

---

# 📂 Project Structure

```text
Meet-Mind-AI/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       │   ├── meetings/
│       │   └── chat/
│       │
│       ├── services/
│       │   ├── pipeline/
│       │   └── database/
│       │
│       └── models/
│           └── database schemas
│
├── core/
│   ├── transcriber.py
│   ├── extractor.py
│   ├── vector_store.py
│   └── rag_engine.py
│
├── utils/
│   └── audio_processor.py
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       └── ...
│
├── requirements.txt
├── .env.example
└── README.md
```

---

# 🛠️ Tech Stack

**Frontend**

- React
- Vite
- JavaScript

**Backend**

- Python
- FastAPI
- SQLAlchemy

**AI / ML**

- OpenAI Whisper
- PyTorch
- CUDA
- HuggingFace Embeddings
- Sarvam AI

**Generative AI**

- Groq
- `openai/gpt-oss-120b`

**RAG**

- LangChain
- ChromaDB

**Media Processing**

- yt-dlp
- FFmpeg

---

# ⚙️ Prerequisites

- Python 3.11 or 3.12
- Node.js 18+
- FFmpeg
- NVIDIA GPU with CUDA support *(optional but recommended)*
- Groq API key
- Sarvam API key *(required for Hinglish transcription)*

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/Pratham31-coder/Meet-Mind-AI.git

cd Meet-Mind-AI
```

## 2. Create Python Environment

### Windows

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

For CUDA-enabled PyTorch:

```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
SARVAM_API_KEY=your_sarvam_api_key

WHISPER_MODEL=small
```

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | LLM inference, summarization, extraction and RAG |
| `SARVAM_API_KEY` | Hinglish transcription |
| `WHISPER_MODEL` | Local Whisper model size |

Supported Whisper models:

```text
tiny
base
small
medium
large
```

---

# 🖥️ Run the Application

### Start Backend

From the project root:

```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Start Frontend

```bash
cd frontend

npm install

npm run dev
```

Application:

```text
http://localhost:5173
```

---

# 📈 Future Improvements

Planned improvements include:

- Speaker identification and diarization
- Multi-meeting search
- Meeting comparison
- Automatic follow-up email generation
- Calendar integration
- Persistent user accounts
- Export summaries to PDF / Markdown
- More Indian-language transcription support
- Improved citation and source tracking for RAG responses

---

# 🎓 What I Learned Building MeetMind

Building MeetMind required combining multiple areas of modern AI engineering:

- Building production-style FastAPI APIs
- React frontend development
- Audio/video processing
- GPU inference with CUDA
- Speech recognition
- LLM integration
- Structured information extraction
- Embedding generation
- Vector databases
- LangChain RAG pipelines
- Retrieval optimization
- Managing local AI models
- Connecting multiple AI services into one pipeline

The biggest challenge was not calling an LLM API — it was **designing an end-to-end system where media processing, transcription, information extraction, vector retrieval, and conversational AI work together reliably.**

---

# 📜 License

Personal / portfolio project.
