FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Dependencies install
COPY requirements.txt .

# Pip upgrade + install
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir openai-whisper

# Whisper model pre-download
RUN python -c "import whisper; whisper.load_model('base'); print('Whisper OK')"

# App code copy
COPY . .

# Storage directories
RUN mkdir -p storage/uploads storage/audio storage/outputs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]