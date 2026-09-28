# MeetMind AI

Turn a YouTube video or local audio/video file into meeting notes you can chat with.

MeetMind AI transcribes the recording, generates a title and summary, extracts action items, key decisions, and open questions, then builds a local knowledge base so you can ask follow-up questions about the meeting.

## What it does

1. Accepts a **YouTube URL** or a **local file path**.
2. Downloads or converts the audio (WAV, 16 kHz, mono).
3. Splits audio into chunks and transcribes it.
4. Uses an LLM to produce:
   - Meeting title
   - Summary
   - Action items
   - Key decisions
   - Open questions
5. Stores the transcript in **Chroma** for retrieval-augmented Q&A.
6. Lets you chat with the meeting in the terminal.

**Transcription**

- `english` → local [OpenAI Whisper](https://github.com/openai/whisper)
- `hinglish` → [Sarvam](https://www.sarvam.ai/) speech-to-text translate (other 22 languages+ transcript)

**Language models**

- Gemini for title, summary, and extraction
- Mistral for RAG chat

## Pipeline

```text
YouTube URL or local file
        ↓
   Audio extract / convert
        ↓
      Chunk audio
        ↓
  Whisper or Sarvam STT
        ↓
        Transcript
        ├── Gemini → title, summary, actions, decisions, questions
        └── Chroma + MiniLM embeddings
                    ↓
              Mistral RAG chat
```

## Project structure

```text
main.py                 CLI entry point
core/
  transcriber.py        Whisper / Sarvam
  summarizer.py         Title and summary (Gemini)
  extractor.py          Actions, decisions, questions (Gemini)
  vector_store.py       Chroma vector store
  rag_engine.py         LangChain RAG chain (Mistral)
utils/
  audio_processor.py    yt-dlp download, convert, chunk
.env.example            Environment variable template
```

## Prerequisites

- Python 3.11 or 3.12 recommended
- [FFmpeg](https://ffmpeg.org/) on your PATH (required by `yt-dlp` and `pydub`)
- API keys: Gemini, Mistral, and Sarvam (Sarvam only if you use hinglish)

## Setup

```bash
git clone https://github.com/Pratham31-coder/Meet-Mind-AI.git
cd Meet-Mind-AI
python -m venv .venv
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install python-dotenv pydub langchain-google-genai langchain-chroma requests
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
pip install python-dotenv pydub langchain-google-genai langchain-chroma requests
```

Copy the env template and add your keys (never commit `.env`):

```powershell
copy .env.example .env
```

```bash
cp .env.example .env
```

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Title, summary, action items, decisions, questions |
| `MISTRAL_API_KEY` | Chat over the transcript (RAG) |
| `SARVAM_API_KEY` | Hinglish transcription |
| `WHISPER_MODEL` | Local Whisper size (`tiny`, `base`, `small`, `medium`, `large`). Default: `small` |
| `SARVAM_STT_MODEL` | Sarvam model. Default: `saaras:v3` |

The first Whisper run downloads the model weights. Embeddings use `all-MiniLM-L6-v2` on CPU.

## Run

```bash
python main.py
```

You will be prompted for:

1. A YouTube URL or a local audio/video path
2. Language: `english` or `hinglish` (press Enter for English)

After processing, the CLI prints the title, summary, action items, decisions, and questions. Then you can ask questions about the meeting. Type `exit`, `quit`, or `q` to stop.

Long videos take several minutes: download/convert, Whisper on CPU, and multiple LLM calls.

## Notes

- Downloaded audio and chunks are written under `downloades/` and are gitignored.
- The vector store is written to `vector_db/` (also gitignored). The current CLI uses a single Chroma collection, so a new run shares that store.
- `app.py` is a placeholder. A FastAPI + React web app is planned; the CLI pipeline above is the working product today.

## License

Personal / portfolio project.
