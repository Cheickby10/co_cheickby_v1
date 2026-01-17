from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
from typing import List, Dict, Any

app = FastAPI()

# --- CONFIG ADMIN ---
ADMIN_KEY = "CHEICKBYPRO"

# --- LOGS EN MÉMOIRE ---
game_logs: List[Dict[str, Any]] = []

# --- PROFILS DE JOUEUR ---
def detect_profile(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["safe", "prudent", "sécurisé", "calme"]):
        return "safe"
    if any(w in msg for w in ["hardcore", "all in", "all_in", "agressif", "risqué"]):
        return "aggressive"
    return "balanced"

def compute_option_score(option, profile: str):
    survival = option["survival_chance"]
    min_s, max_s = option["score_range"]
    potential_score = (min_s + max_s) / 10.0
    risk = option["risk"]

    if profile == "safe":
        risk_factor = 1 - risk
    elif profile == "aggressive":
        risk_factor = risk
    else:
        risk_factor = 1 - abs(risk - 0.5)

    global_score = survival * 0.6 + potential_score * 0.3 + risk_factor * 0.1
    return global_score

# --- LOGIQUE PAR JEU ---
# (wild_west, kamikaze, dragons_gold, royal_feast)
# Tes fonctions predict_* restent inchangées

# --- PREDICT GAME ---
def predict_game(game: str, profile: str):
    game = game.lower()
    if game == "wild_west":
        return predict_wild_west(profile)
    if game == "kamikaze":
        return predict_kamikaze(profile)
    if game == "dragons_gold":
        return predict_dragons_gold(profile)
    if game == "royal_feast":
        return predict_royal_feast(profile)
    return {
        "game": game,
        "best_path": None,
        "survival_chance": None,
        "predicted_score": None,
        "reason": "Je ne connais pas encore ce jeu, mais je peux apprendre.",
        "profile": profile
    }

def log_game(event_type: str, game: str, profile: str, prediction: dict):
    game_logs.append({
        "type": event_type,
        "game": prediction.get("game", game),
        "profile": profile,
        "best_path": prediction.get("best_path"),
        "predicted_score": prediction.get("predicted_score"),
        "survival_chance": prediction.get("survival_chance"),
        "reason": prediction.get("reason")
    })
    if len(game_logs) > 200:
        game_logs.pop(0)

# --- ENDPOINTS CLASSIQUES ---
@app.get("/start")
def start(game: str, profile: str = "balanced"):
    prediction = predict_game(game, profile)
    log_game("start", game, profile, prediction)
    return JSONResponse(content={
        "message": f"Bienvenue dans {prediction['game']} !",
        "profile": prediction["profile"],
        "best_path": prediction["best_path"],
        "survival_chance": f"{prediction['survival_chance']}%",
        "predicted_score": prediction["predicted_score"],
        "reason": prediction["reason"]
    })

@app.get("/action")
def action(game: str, profile: str = "balanced"):
    prediction = predict_game(game, profile)
    survived = prediction["survival_chance"] is not None and prediction["survival_chance"] >= 50
    log_game("action", game, profile, prediction)
    return JSONResponse(content={
        "game": prediction["game"],
        "profile": prediction["profile"],
        "best_path": prediction["best_path"],
        "predicted_score": prediction["predicted_score"],
        "survival_chance": f"{prediction['survival_chance']}%",
        "survived": survived,
        "reason": prediction["reason"]
    })

# --- HANDLER POUR POE ---
@app.post("/")
async def poe_handler(request: Request):
    data = await request.json()
    message = data.get("message", "").strip()
    lower_msg = message.lower()

    profile = detect_profile(lower_msg)

    if lower_msg.startswith("start"):
        game = lower_msg.replace("start", "").strip().replace(" ", "_")
        prediction = predict_game(game, profile)
        log_game("start_poe", game, profile, prediction)
        return JSONResponse(content={
            "type": "start",
            "game": prediction["game"],
            "profile": prediction["profile"],
            "best_path": prediction["best_path"],
            "survival_chance": f"{prediction['survival_chance']}%",
            "predicted_score": prediction["predicted_score"],
            "reason": prediction["reason"],
            "message": f"Profil détecté : {prediction['profile']}. Chemin conseillé : '{prediction['best_path']}' avec {prediction['survival_chance']} de survie."
        })

    if lower_msg.startswith("action"):
        game = lower_msg.replace("action", "").strip().replace(" ", "_")
        prediction = predict_game(game, profile)
        survived = prediction["survival_chance"] is not None and prediction["survival_chance"] >= 50
        log_game("action_poe", game, profile, prediction)
        return JSONResponse(content={
            "type": "action",
            "game": prediction["game"],
            "profile": prediction["profile"],
            "best_path": prediction["best_path"],
            "predicted_score": prediction["predicted_score"],
            "survival_chance": f"{prediction['survival_chance']}%",
            "survived": survived,
            "reason": prediction["reason"],
            "message": f"Profil {prediction['profile']} : je te recommande '{prediction['best_path']}' ({prediction['survival_chance']} de survie)."
        })

    return JSONResponse(content={
        "message": "Commande inconnue. Utilise par exemple : 'start wild_west', 'action dragons_gold', éventuellement avec des mots comme 'safe' ou 'hardcore'."
    })

# --- STATIC FILES & UI / ADMIN ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

# Page d’accueil
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Interface utilisateur
@app.get("/ui", response_class=HTMLResponse)
async def ui_page(request: Request):
    return templates.TemplateResponse("ui.html", {"request": request})

# Dashboard admin
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, key: str = Query(None)):
    if key != ADMIN_KEY:
        return HTMLResponse("<h1>Accès refusé</h1><p>Clé invalide.</p>", status_code=403)
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/admin/data")
async def admin_data(key: str = Query(None)):
    if key != ADMIN_KEY:
        return JSONResponse({"error": "Clé invalide"}, status_code=403)
    total = len(game_logs)
    by_game = {}
    by_profile = {}
    for log in game_logs:
        g = log["game"]
        p = log["profile"]
        by_game[g] = by_game.get(g, 0) + 1
        by_profile[p] = by_profile.get(p, 0) + 1
    return JSONResponse({
        "total": total,
        "by_game": by_game,
        "by_profile": by_profile,
        "logs": game_logs[-50:]
    })
