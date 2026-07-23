import os
import asyncio
import requests
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ==========================================
# 1. CRÉATION AUTOMATIQUE DES DOSSIERS
# ==========================================
# Nécessaire pour éviter les erreurs "Directory not found" sur Render
os.makedirs("temp", exist_ok=True)
os.makedirs("config", exist_ok=True)
os.makedirs("chrome_session", exist_ok=True)

# ==========================================
# 2. GESTION DES RESSOURCES ET POLICES
# ==========================================
FONT_FILE = os.path.join("temp", "Roboto-Bold.ttf")

if not os.path.exists(FONT_FILE):
    try:
        font_url = "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Bold.ttf"
        response = requests.get(font_url, timeout=10)
        if response.status_code == 200:
            with open(FONT_FILE, "wb") as f:
                f.write(response.content)
            print("Police Roboto-Bold téléchargée avec succès.")
        else:
            FONT_FILE = None
    except Exception as e:
        print(f"Impossible de télécharger la police : {e}")
        FONT_FILE = None

# ==========================================
# 3. INITIALISATION FASTAPI
# ==========================================
app = FastAPI(
    title="Infinity AI Auto Engine",
    description="API d'automation et de génération vidéo IA",
    version="1.0.0"
)

# Configuration CORS pour autoriser toutes les origines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 4. MODÈLES DE DONNÉES (PYDANTIC)
# ==========================================
class AgentRequest(BaseModel):
    niche: str = "Général"
    target_country: str = "FR"
    use_proxy: bool = False
    proxy_url: Optional[str] = None
    user_prompt: Optional[str] = ""

class AgentState:
    def __init__(self, niche, target_country, use_proxy, proxy_url, use_avatar, source_url, user_prompt, script, audio_url, video_path, status, youtube_status):
        self.niche = niche
        self.target_country = target_country
        self.use_proxy = use_proxy
        self.proxy_url = proxy_url
        self.use_avatar = use_avatar
        self.source_url = source_url
        self.user_prompt = user_prompt
        self.script = script
        self.audio_url = audio_url
        self.video_path = video_path
        self.status = status
        self.youtube_status = youtube_status

# ==========================================
# 5. MOTEUR EXÉCUTION / LOGIQUE BOT
# ==========================================
def run_sync_task(state: AgentState):
    """Fonction exécutée en arrière-plan pour traiter la vidéo."""
    try:
        print(f"Début du traitement pour la niche : {state.niche}")
        # Insérez ici la logique globale de génération / Selenium / MoviePy
        # ...
        state.status = "Terminé"
        print("Traitement terminé avec succès.")
    except Exception as e:
        state.status = f"Erreur : {str(e)}"
        print(f"Erreur pendant l'exécution : {e}")

# ==========================================
# 6. ROUTES DE L'API
# ==========================================
@app.get("/")
def root():
    """Route racine pour vérifier si le serveur est en ligne."""
    return {
        "status": "Infinity Engine Online",
        "agents_count": 9,
        "cloud_mode": True,
        "system": "Docker / Render OK"
    }

@app.get("/health")
def health_check():
    """Vérification de santé de l'instance."""
    return {"status": "healthy"}

@app.post("/generate")
async def generate_content(req: AgentRequest, background_tasks: BackgroundTasks):
    """Déclenche la génération de vidéo en arrière-plan."""
    state = AgentState(
        niche=req.niche,
        target_country=req.target_country,
        use_proxy=req.use_proxy,
        proxy_url=req.proxy_url,
        use_avatar=False,
        source_url=None,
        user_prompt=req.user_prompt,
        script="",
        audio_url="",
        video_path="",
        status="Initié",
        youtube_status="En attente"
    )
    
    # Exécution de la tâche lourde en tâche de fond (non bloquante)
    background_tasks.add_task(run_sync_task, state)
    
    return {
        "status": "Génération manuelle lancée en arrière-plan.",
        "niche": req.niche,
        "target_country": req.target_country
    }

# ==========================================
# 7. POINT D'ENTRÉE LOCAL
# ==========================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
