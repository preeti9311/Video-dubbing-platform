# Video-dubbing-platform

# 🎬 AI-Powered Video Dubbing Platform

An end-to-end AI pipeline that automatically dubs videos into any language using
Whisper (speech recognition), Google Translate, and gTTS (text-to-speech).

Built as an internship assignment project.

---

## 🚀 Live Demo

> Upload a video → AI transcribes → Translates → Generates dubbed voice → Download!

---

## 🧠 How It Works

Video Upload
↓
Whisper AI  →  Speech to Text
↓
Google Translate  →  Target Language Text
↓
gTTS  →  Dubbed Audio
↓
FFmpeg  →  Merge Audio + Video
↓
Download Dubbed Video ✅

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Speech-to-Text | OpenAI Whisper |
| Translation | deep-translator (Google) |
| Text-to-Speech | gTTS |
| Video Processing | FFmpeg |
| Frontend | HTML + CSS + Vanilla JS |
| Containerization | Docker + docker-compose |

---

## 📁 Project Structure

video-dubbing-platform/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Settings
│   ├── api/
│   │   ├── upload.py        # Upload endpoint
│   │   ├── status.py        # Status endpoint
│   │   └── download.py      # Download endpoint
│   ├── services/
│   │   ├── transcription.py # Whisper STT
│   │   ├── translation.py   # Text translation
│   │   ├── tts.py           # Text-to-speech
│   │   └── merger.py        # FFmpeg merge
│   ├── models/
│   │   └── schemas.py       # Pydantic schemas
│   ├── utils/
│   │   ├── file_handler.py  # File operations
│   │   └── job_store.py     # In-memory job tracking
│   └── static/
│       └── index.html       # Frontend UI
├── storage/
│   ├── uploads/             # Incoming videos
│   ├── audio/               # Intermediate audio
│   └── outputs/             # Final dubbed videos
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

---

## ⚙️ Setup & Installation

### Option 1: Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/video-dubbing-platform.git
cd video-dubbing-platform

# Copy environment file
cp .env.example .env

# Build and run
docker-compose up --build
```

Open: http://localhost:8000

---

### Option 2: Local Setup

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/video-dubbing-platform.git
cd video-dubbing-platform

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg
sudo apt-get install ffmpeg -y   # Linux
brew install ffmpeg               # Mac

# Copy env file
cp .env.example .env

# Run server
uvicorn app.main:app --reload --port 8000
```

Open: http://localhost:8000

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/upload` | Upload video for dubbing |
| `GET` | `/api/v1/status/{job_id}` | Check processing status |
| `GET` | `/api/v1/download/{job_id}` | Download dubbed video |
| `GET` | `/api/v1/jobs` | List all jobs (debug) |
| `GET` | `/docs` | Swagger UI |

---

## 🌍 Supported Languages

| Code | Language |
|------|----------|
| `hi` | Hindi |
| `es` | Spanish |
| `fr` | French |
| `de` | German |
| `ja` | Japanese |
| `ko` | Korean |
| `zh-cn` | Chinese |
| `ar` | Arabic |
| `pt` | Portuguese |
| `ru` | Russian |

---

## 📸 Screenshots

> Add screenshots here after running the project

---

## 🔧 Environment Variables

```env
DEBUG=True
WHISPER_MODEL=base
DEFAULT_TARGET_LANGUAGE=hi
```

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `True` | Debug mode |
| `WHISPER_MODEL` | `base` | Whisper model size |
| `DEFAULT_TARGET_LANGUAGE` | `hi` | Default dub language |

---

## 🗺️ Roadmap

- [x] Video upload API
- [x] Whisper transcription
- [x] Multi-language translation
- [x] Text-to-speech dubbing
- [x] FFmpeg video merge
- [x] Clean frontend UI
- [x] Docker support
- [ ] ElevenLabs voice support
- [ ] Celery + Redis async queue
- [ ] Multiple speaker detection
- [ ] Subtitle generation (.srt)

---
## 🌐 Live Demo
🚀 https://video-dubbing-platform.onrender.com

## 👩‍💻 Author

**Preeti**  
Backend Developer Intern  
Built with ❤️ using FastAPI + Whisper + gTTS