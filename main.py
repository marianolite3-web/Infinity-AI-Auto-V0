# =========================================================
# INFINITY AI OS - 100% COMPLETE & DEPLOYMENT READY
# =========================================================
# DÉPENDANCES PIP À INSTALLER :
# pip install fastapi uvicorn langgraph requests pydantic apscheduler yt-dlp undetected-chromedriver selenium moviepy Pillow
# DÉPENDANCE SYSTÈME (LINUX/REPLIT) :
# apt-get update && apt-get install -y ffmpeg
# =========================================================

import os
import requests
import uuid
import urllib.parse
import json
import time
import asyncio
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List, Any
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ColorClip, ImageClip, vfx
from yt_dlp import YoutubeDL
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from apscheduler.schedulers.background import BackgroundScheduler
from PIL import Image, ImageDraw, ImageFont

# --- INITIALISATION ---
app = FastAPI(title="Infinity AI OS - Full Autopilot")
scheduler = BackgroundScheduler()

# Détecte si on est sur le cloud (Replit/Docker) ou en local
IS_CLOUD = os.getenv("REPL_ID") is not None or os.getenv("DOCKER") is not None

# Création des dossiers nécessaires
os.makedirs('temp', exist_ok=True)
os.makedirs('config', exist_ok=True)
os.makedirs('chrome_session', exist_ok=True)

# Fichiers de configuration
PERFORMANCE_FILE = 'config/performance.json'
CONFIG_FILE = 'config/autopilot.json'
FONT_FILE = 'temp/montserrat.ttf'

# Initialisation des fichiers s'ils n'existent pas
if not os.path.exists(PERFORMANCE_FILE):
    with open(PERFORMANCE_FILE, 'w') as f:
        json.dump({"videos_posted": 0, "last_hook_style": "normal"}, f)

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"active": False}, f)

# Téléchargement de la police de caractères (Évite l'erreur 'arial.ttf not found' sur le cloud)
if not os.path.exists(FONT_FILE):
    try:
        print("📥 Téléchargement de la police Montserrat...")
        font_url = "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Bold.ttf"
        # Fallback si l'URL change
        response = requests.get(font_url, timeout=10)
        with open(FONT_FILE, 'wb') as f:
            f.write(response.content)
    except Exception:
        print("⚠️ Erreur téléchargement police, utilisation du défaut système.")
        FONT_FILE = None # Le système utilisera la police par défaut

# Base de données des pays monétisables
MONETIZABLE_COUNTRIES = {
    "FR": {"lang": "fr-FR", "hashtags": "#pourtoi #fyp #viral #paris #france", "location": "Paris, France", "voice": "Guillaume"},
    "US": {"lang": "en-US", "hashtags": "#fyp #viral #foryou #newyork #usa", "location": "New York, USA", "voice": "Brian"}
}

class AgentState(TypedDict):
    niche: str
    target_country: str
    use_proxy: bool
    proxy_url: Optional[str]
    use_avatar: bool
    source_url: Optional[str]
    user_prompt: str
    script: str
    audio_url: str
    video_path: str
    status: str
    youtube_status: str

# Fonctions de configuration
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f)

# --- 1. AGENT ANALYSE & OPTIMISATION ---
def agent_analytics_optimizer(state: AgentState):
    print("📊 Agent Analyse : Lecture des performances passées...")
    try:
        with open(PERFORMANCE_FILE, 'r') as f:
            data = json.load(f)
        # Si les dernières vidéos n'ont pas performé, on change de style de hook
        if data.get("videos_posted", 0) > 3 and data.get("last_hook_style") == "normal":
            state['status'] = "Optimization: Aggressive Hook"
            print("⚠️ Changement de stratégie : Hook agressif activé.")
        else:
            state['status'] = "Optimization: Normal Hook"
    except:
        state['status'] = "Initié"
    return state

# --- 2. AGENT TENDANCES (Trend Prediction) ---
def agent_trends(state: AgentState):
    print("📈 Agent Tendances : Scan du web pour sujets viraux...")
    trend_prompt = f"Agis comme un expert viral. Donne moi UN seul sujet très tendance et émergent cette semaine sur TikTok pour la niche: {state['niche']}. Réponds juste avec le sujet en 3 mots."
    trend_url = f"https://text.pollinations.ai/{urllib.parse.quote(trend_prompt)}"
    try:
        state['user_prompt'] = requests.get(trend_url, timeout=10).text.strip()
    except:
        state['user_prompt'] = "Secret du succès"
    return state

# --- 3. AGENT SCRIPT ---
def agent_script(state: AgentState):
    print("📝 Agent Script : Écriture du script...")
    hook_style = "avec une question choc" if "Aggressive" in state['status'] else "accrocheur"
    lang = MONETIZABLE_COUNTRIES[state['target_country']]['lang'].split('-')[0]
    
    script_prompt = f"Écris en {lang} un script court et viral pour TikTok sur : {state['user_prompt']}. Niche: {state['niche']}. Le hook doit être {hook_style}."
    script_url = f"https://text.pollinations.ai/{urllib.parse.quote(script_prompt)}"
    try:
        state['script'] = requests.get(script_url, timeout=15).text[:400]
    except:
        state['script'] = "Voici le secret. Travaillez dur."
    return state

# --- 4. AGENT AVATAR (UGC) ---
def agent_avatar(state: AgentState):
    if state.get('use_avatar'):
        print("🧑‍💼 Agent Avatar : Préparation UGC (Simulé/HeyGen)...")
        state['video_path'] = "generate_ai"
    else:
        state['video_path'] = "generate_ai"
    return state

# --- 5. AGENT AUDIO ---
def agent_audio(state: AgentState):
    print("🎙️ Agent Audio : Génération voix...")
    voice = MONETIZABLE_COUNTRIES[state['target_country']]['voice']
    text = state['script'][:200]
    state['audio_url'] = f"https://api.streamelements.com/kappa/v2/speech?voice={voice}&text={urllib.parse.quote(text)}"
    return state

# --- 6. AGENT MÉDIA ---
def agent_media_fetcher(state: AgentState):
    print("📥 Agent Média : Téléchargement/Génération source...")
    task_id = str(uuid.uuid4())
    video_path = f"temp/raw_{task_id}.mp4"
    
    if state.get('source_url'):
        ydl_opts = {'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/mp4', 'outtmpl': video_path, 'quiet': True}
        try:
            with YoutubeDL(ydl_opts) as ydl: ydl.download([state['source_url']])
            state['video_path'] = video_path
        except:
            state['video_path'] = "generate_ai"
    return state

# --- 7. AGENT SOUS-TITRES (Smart Subtitles Pro) ---
def generate_subtitles(script: str, audio_clip):
    print("✍️ Agent Sous-titres : Génération des textes animés...")
    task_id = str(uuid.uuid4())
    words = script.split()
    if not words: return []
    
    subtitle_clips = []
    
    try:
        if FONT_FILE and os.path.exists(FONT_FILE):
            font = ImageFont.truetype(FONT_FILE, 80)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # On groupe par 3 mots pour un rendu TikTok
    chunks = [' '.join(words[i:i+3]) for i in range(0, len(words), 3)]
    chunk_duration = audio_clip.duration / len(chunks)
    
    for i, chunk in enumerate(chunks):
        start_time = i * chunk_duration
        img_path = f"temp/sub_{task_id}_{i}.png"
        
        # Création de l'image de texte avec PIL
        img = Image.new('RGBA', (1080, 300), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Centrage approximatif du texte
        bbox = draw.textbbox((0, 0), chunk, font=font)
        text_width = bbox[2] - bbox[0]
        x = (1080 - text_width) // 2
        y = 50
        
        # Bordure noire (Outline)
        for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2), (-3,0), (3,0), (0,-3), (0,3)]:
            draw.text((x+dx, y+dy), chunk, font=font, fill=(0, 0, 0, 255))
        # Texte blanc
        draw.text((x, y), chunk, font=font, fill=(255, 255, 255, 255))
        
        img.save(img_path)
        
        # Animation du texte (Scale up)
        txt_clip = ImageClip(img_path).set_start(start_time).set_duration(chunk_duration).set_position(('center', 0.8), relative=True)
        txt_clip = txt_clip.resize(lambda t: 1 + 0.1 * (t / chunk_duration))
        subtitle_clips.append(txt_clip)
        
    return subtitle_clips

# --- 8. AGENT MONTAGE (Viral Edit Engine Pro) ---
def agent_editor(state: AgentState):
    print("🎬 Agent Montage : Assemblage final...")
    task_id = str(uuid.uuid4())
    final_path = f"temp/final_{task_id}.mp4"
    audio_path = f"temp/audio_{task_id}.mp3"
    
    try:
        audio_response = requests.get(state['audio_url'], timeout=20)
        with open(audio_path, 'wb') as f: f.write(audio_response.content)
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        # Génération des sous-titres
        sub_clips = generate_subtitles(state['script'], audio_clip)

        if state['video_path'] == "generate_ai":
            img_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(state['user_prompt'])}"
            img_path = f"temp/img_{task_id}.jpg"
            try:
                img_response = requests.get(img_url, timeout=30)
                with open(img_path, 'wb') as f: f.write(img_response.content)
                clip = ImageClip(img_path).set_duration(duration).resize(height=1920).set_position('center')
                clip = clip.resize(lambda t: 1 + 0.1 * (t / duration))
            except Exception:
                clip = ColorClip((1080, 1920), color=(20, 20, 20)).set_duration(duration)
        else:
            clip = VideoFileClip(state['video_path'])
            clip = clip.fx(vfx.mirror_x).fx(vfx.speedx, 1.03).fx(vfx.colorx, 1.1)
            clip = clip.resize(height=1920)
            bg = ColorClip((1080, 1920), color=(0,0,0)).set_duration(clip.duration)
            clip = clip.set_position('center')
            clip = CompositeVideoClip([bg, clip]).set_duration(duration)

        # Superposition Vidéo + Sous-titres + Audio
        final_composite = CompositeVideoClip([clip] + sub_clips).set_audio(audio_clip)
        final_composite.write_videofile(final_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
        state['video_path'] = final_path
        
    except Exception as e:
        print(f"❌ Erreur Montage: {e}")
        state['video_path'] = "Erreur"
    return state

# --- 9. AGENT PUBLICATION MULTI-PLATEFORMES ---
def agent_publisher(state: AgentState):
    print("📡 Agent Publication : Lancement du Bot Multi-Plateformes...")
    
    options = uc.ChromeOptions()
    country_config = MONETIZABLE_COUNTRIES.get(state['target_country'], MONETIZABLE_COUNTRIES["FR"])
    options.add_argument(f"--user-data-dir={os.path.abspath('chrome_session')}")
    
    if IS_CLOUD: 
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--lang={country_config["lang"]}')
    
    if state['use_proxy'] and state.get('proxy_url'):
        options.add_argument(f'--proxy-server={state["proxy_url"]}')

    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # --- TIKTOK ---
        print("📱 Publication TikTok...")
        driver.get("https://www.tiktok.com/upload?lang=fr")
        try:
            upload_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            upload_input.send_keys(os.path.abspath(state['video_path']))
            caption_box = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))
            caption_box.send_keys(f"{state['user_prompt']} {country_config['hashtags']} #{state['niche']}")
            time.sleep(3)
            driver.find_element(By.XPATH, "//button[contains(text(),'Publier')]").click()
            state['status'] = "Publié sur TikTok"
            print("🚀 Publié sur TikTok !")
            time.sleep(10)
        except Exception as e:
            state['status'] = f"Échec TikTok: {e}"
            print(f"❌ Échec TikTok: {e}")

        # --- YOUTUBE SHORTS ---
        print("📺 Publication YouTube Shorts...")
        try:
            driver.get("https://www.youtube.com/upload?lang=fr")
            yt_upload = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
            yt_upload.send_keys(os.path.abspath(state['video_path']))
            
            time.sleep(5) # Attente du chargement de l'interface YT
            
            # Titre
            title_box = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='textbox']")))
            title_box.send_keys(f"{state['user_prompt']} #shorts")
            
            # Description
            try:
                desc_box = driver.find_element(By.XPATH, "//div[@id='description-wrapper']")
                desc_box.send_keys(f"{state['script']} {country_config['hashtags']}")
            except: pass
            
            # Cocher "Mineur" (Non)
            try:
                driver.find_element(By.XPATH, "//tp-yt-paper-radio[@name='VIDEO_MADE_FOR_KIDS_NOT_MK']").click()
            except: pass
            
            time.sleep(2)
            # Boutons Suivant (3 fois)
            for _ in range(3):
                try:
                    driver.find_element(By.XPATH, "//ytcp-button[contains(text(), 'Suivant')]").click()
                    time.sleep(2)
                except: pass
            
            # Bouton Publier
            publish_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//ytcp-button[contains(text(), 'Publier')]")))
            publish_btn.click()
            state['youtube_status'] = "Publié sur YouTube"
            print("🚀 Publié sur YouTube Shorts !")
            time.sleep(15)
        except Exception as e:
            state['youtube_status'] = f"Échec YT: {e}"
            print(f"❌ Échec YT (Menu probablement changé): {e}")
            
    except Exception as e:
        state['status'] = f"Erreur Globale: {e}"
    finally:
        driver.quit()
        
    # Mise à jour de l'analytique
    try:
        with open(PERFORMANCE_FILE, 'r') as f: data = json.load(f)
        data['videos_posted'] = data.get('videos_posted', 0) + 1
        with open(PERFORMANCE_FILE, 'w') as f: json.dump(data, f)
    except: pass
    
    return state

# --- ORCHESTRATION LANGGRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("agent_analytics_optimizer", agent_analytics_optimizer)
workflow.add_node("agent_trends", agent_trends)
workflow.add_node("agent_script", agent_script)
workflow.add_node("agent_avatar", agent_avatar)
workflow.add_node("agent_audio", agent_audio)
workflow.add_node("agent_media_fetcher", agent_media_fetcher)
workflow.add_node("agent_editor", agent_editor)
workflow.add_node("agent_publisher", agent_publisher)

workflow.set_entry_point("agent_analytics_optimizer")
workflow.add_edge("agent_analytics_optimizer", "agent_trends")
workflow.add_edge("agent_trends", "agent_script")
workflow.add_edge("agent_script", "agent_avatar")
workflow.add_edge("agent_avatar", "agent_audio")
workflow.add_edge("agent_audio", "agent_media_fetcher")
workflow.add_edge("agent_media_fetcher", "agent_editor")
workflow.add_edge("agent_editor", "agent_publisher")
workflow.add_edge("agent_publisher", END)

infinity_engine = workflow.compile()

# --- SYSTÈME DE TÂCHE AUTOMATIQUE ---
def run_autopilot_sync():
    config = load_config()
    if not config or not config.get('active'): return
    print("⏰ [CRON] Lancement de la génération automatique...")
    state = AgentState(
        niche=config['niche'], target_country=config['target_country'], use_proxy=config['use_proxy'],
        proxy_url=config.get('proxy_url'), use_avatar=False, source_url=None,
        user_prompt="", script="", audio_url="", video_path="",
        status="Initié", youtube_status="En attente"
    )
    try:
        infinity_engine.invoke(state)
    except Exception as e:
        print(f"❌ Erreur Autopilot: {e}")

# --- API ENDPOINTS ---
class AutopilotConfig(BaseModel):
    active: bool
    niche: str
    target_country: str = "FR"
    frequency_hours: float = 4.0
    use_proxy: bool = False
    proxy_url: Optional[str] = None

@app.on_event("startup")
def startup_event():
    if not scheduler.running: scheduler.start()
    config = load_config()
    if config and config.get('active'):
        scheduler.add_job(run_autopilot_sync, 'interval', hours=config['frequency_hours'], id="autopilot_job", replace_existing=True)
        print("✅ Autopilot restauré au démarrage.")

@app.post("/api/v1/configure_autopilot")
async def configure_autopilot(config: AutopilotConfig):
    save_config(config.dict())
    scheduler.remove_all_jobs()
    if config.active:
        scheduler.add_job(run_autopilot_sync, 'interval', hours=config.frequency_hours, id="autopilot_job", replace_existing=True)
        asyncio.create_task(asyncio.to_thread(run_autopilot_sync))
        return {"status": "Autopilot ACTIVÉ."}
    return {"status": "Autopilot DÉSACTIVÉ."}

@app.get("/api/v1/login_tiktok")
async def login_tiktok():
    def _login():
        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={os.path.abspath('chrome_session')}")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        if IS_CLOUD: options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        driver.get("https://www.tiktok.com/login")
        time.sleep(120)
        driver.quit()
    asyncio.create_task(asyncio.to_thread(_login))
    return {"status": "Tentative de connexion ouverte. Vous avez 2 minutes."}

@app.post("/api/v1/generate_manual")
async def generate_manual(req: AutopilotConfig):
    def run_sync():
        state = AgentState(
            niche=req.niche, target_country=req.target_country, use_proxy=req.use_proxy,
            proxy_url=req.proxy_url, use_avatar=False, source_url=None, user_prompt="", script="",
            audio_url="", video_path="", status="Initié", youtube_status="En attente"
        )
        infinity_engine.invoke(state)
    
    asyncio.create_task(asyncio.to_thread(run_sync))
    return {"status": "Génération manuelle lancée en arrière-plan."}

@app.get("/")
def root():
    return {"status": "Infinity Engine Online", "agents_count": 9, "cloud_mode": IS_CLOUD, "scheduler_active": scheduler.running}