# MeetMind AI 🚀

Turn a YouTube video or local audio/video file into comprehensive meeting notes you can chat with—powered by **GPU-accelerated** transcription and lightning-fast **Groq LLM** inference.

MeetMind AI transcribes your recording on your local NVIDIA GPU, generates a title and summary, extracts action items, key decisions, and open questions, and then builds a local vector knowledge base so you can ask follow-up questions about the meeting. 

It features a modern **React Frontend** and a **FastAPI Backend**, replacing slow CPU workloads with blazingly fast hardware acceleration.

---

## ✨ What it does

1. Accepts a **YouTube URL** or a **local file path**.
2. Downloads or converts the audio seamlessly (WAV, 16 kHz, mono).
3. Transcribes the audio locally using your GPU.
4. Uses **Groq (`openai/gpt-oss-120b`)** to produce:
   - Meeting title
   - 2-3 paragraph summary
   - Action items (with assignees and deadlines)
   - Key decisions
   - Open questions
5. Stores the transcript in **ChromaDB** using local HuggingFace embeddings.
6. Allows you to chat with your meeting via an interactive Retrieval-Augmented Generation (RAG) UI.

**Transcription**
- `english` → local [OpenAI Whisper](https://github.com/openai/whisper) (Hardware Accelerated via PyTorch CUDA)
- `hinglish` → [Sarvam](https://www.sarvam.ai/) speech-to-text translate (English transcript)

**Language Models**
- **Groq API** handles all summarization, extraction, and RAG chat.

---

## 🏗️ Pipeline Architecture

```text
YouTube URL or Local File
           ↓
 Audio Extraction (yt-dlp/ffmpeg)
           ↓
 GPU-Accelerated Transcription (Whisper CUDA)
           ↓
       Transcript
           ├── Groq API → Title, Summary, Actions, Decisions, Questions
           └── ChromaDB + HuggingFace Embeddings (GPU)
                       ↓
              Interactive RAG Chat (Groq API)
```

## 📂 Project Structure

```text
backend/
  app/
    main.py                 FastAPI application entry point
    api/                    API routing (meetings, chat)
    services/               Background pipeline and DB services
    models/                 SQLAlchemy database schemas
core/
  transcriber.py            Whisper / Sarvam integrations
  extractor.py              Groq structured data extraction
  vector_store.py           Chroma vector store builder
  rag_engine.py             LangChain RAG chain (Groq)
utils/
  audio_processor.py        Audio chunking and conversion
frontend/
  src/                      Vite + React UI components
```

---

## ⚙️ Prerequisites

- Python 3.11 or 3.12
- Node.js (v18+)
- [FFmpeg](https://ffmpeg.org/) installed and added to your system PATH
- **NVIDIA GPU** (Optional but highly recommended for CUDA acceleration)
- API keys: **Groq** (and **Sarvam** if transcribing Hinglish)

---

## 🚀 Setup

### 1. Clone the repository
```bash
git clone https://github.com/Pratham31-coder/Meet-Mind-AI.git
cd Meet-Mind-AI
```

### 2. Backend Setup
Set up your Python virtual environment and install dependencies:

**Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables
Create your `.env` file in the root directory:
```bash
cp .env.example .env
```
Add your keys to the `.env` file:
| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Title, summary, extraction, and RAG chat |
| `SARVAM_API_KEY` | Hinglish transcription |
| `WHISPER_MODEL` | Local Whisper size (`tiny`, `base`, `small`, `medium`, `large`). Default: `small` |

### 4. Frontend Setup
```bash
cd frontend
npm install
```

---

## 🏃‍♂️ Running the Application

You need to run both the FastAPI backend and the React frontend simultaneously.

**Start the Backend:**
```powershell
# From the root directory (ensure your .venv is activated)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

**Start the Frontend:**
```powershell
# From the /frontend directory
npm run dev
```

The application will be live at: **http://localhost:5173**

---

## 📝 Notes

- Large files and chunks are temporarily stored in `backend/data/jobs/` and are automatically cleaned up.
- Vector databases are uniquely created per meeting inside the job directory to ensure accurate RAG retrieval.
- The first run will download the Whisper model and HuggingFace embedding weights. Subsequent runs will use the cached local weights on your GPU.

## 📄 License
Personal / portfolio project.
