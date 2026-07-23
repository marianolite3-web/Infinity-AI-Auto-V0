# Image de base Python sur Linux
FROM python:3.10-slim

# Installation des dépendances système (FFmpeg, Chromium pour Selenium)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    chromium \
    chromium-driver \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Variables d'environnement pour Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

# Installation des bibliothèques Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du code
COPY . .

# Exposition du port web
EXPOSE 10000

# Commande de lancement de l'API FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
