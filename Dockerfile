FROM python:3.10-slim

# Installation des dépendances système complètes (FFmpeg, Chromium, OpenCV/Pillow)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    chromium \
    chromium-driver \
    curl \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Variables d'environnement pour Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du code
COPY . .

# Définition du port par défaut de Render
ENV PORT=10000
EXPOSE 10000

# Commande de lancement avec variable PORT
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
