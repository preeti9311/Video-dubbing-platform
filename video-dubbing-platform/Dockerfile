FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg git curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# setuptools pehle install karo — pkg_resources fix
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Phir whisper install karo
RUN pip install --no-cache-dir openai-whisper

# Baaki requirements install karo
RUN pip install --no-cache-dir -r requirements.txt

# Whisper model download karo
RUN python -c "import whisper; whisper.load_model('base'); print('✅ Whisper OK')"

COPY . .

RUN mkdir -p storage/uploads storage/audio storage/outputs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]