from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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
    survival = option["survival_chance"]  # 0 à 1
    min_s, max_s = option["score_range"]
    potential_score = (min_s + max_s) / 10.0  # approx 0 à 1
    risk = option["risk"]  # 0 à 1

    if profile == "safe":
        risk_factor = 1 - risk
    elif profile == "aggressive":
        risk_factor = risk
    else:
        risk_factor = 1 - abs(risk - 0.5)

    global_score = survival * 0.6 + potential_score * 0.3 + risk_factor * 0.1
    return global_score

# --- LOGIQUE PAR JEU ---

def predict_wild_west(profile: str):
    options = [
        {
            "path": "left",
            "survival_chance": 0.92,
            "score_range": (7, 10),
            "risk": 0.2,
            "reason": "Chemin maîtrisé, tu évites l’embuscade principale."
        },
        {
            "path": "right",
            "survival_chance": 0.65,
            "score_range": (4, 9),
            "risk": 0.6,
            "reason": "Plus risqué, mais parfois très rentable."
        },
        {
            "path": "forward",
            "survival_chance": 0.4,
            "score_range": (2, 10),
            "risk": 0.9,
            "reason": "Tu fonces dans le danger, tout ou rien."
        }
    ]
    best = max(options, key=lambda o: compute_option_score(o, profile))
    score = random.randint(*best["score_range"])
    return {
        "game": "wild_west",
        "best_path": best["path"],
        "survival_chance": round(best["survival_chance"] * 100, 1),
        "predicted_score": score,
        "reason": best["reason"],
        "profile": profile
    }

def predict_kamikaze(profile: str):
    options = [
        {
            "path": "safe_route",
            "survival_chance": 0.88,
            "score_range": (6, 9),
            "risk": 0.3,
            "reason": "Tu limites les risques tout en restant efficace."
        },
        {
            "path": "risky_route",
            "survival_chance": 0.5,
            "score_range": (4, 10),
            "risk": 0.7,
            "reason": "Gros potentiel, mais une erreur et tout explose."
        },
        {
            "path": "all_in",
            "survival_chance": 0.2,
            "score_range": (1, 10),
            "risk": 1.0,
            "reason": "Mode kamikaze total, réservé aux joueurs sans peur."
        }
    ]
    best = max(options, key=lambda o: compute_option_score(o, profile))
    score = random.randint(*best["score_range"])
    return {
        "game": "kamikaze",
        "best_path": best["path"],
        "survival_chance": round(best["survival_chance"] * 100, 1),
        "predicted_score": score,
        "reason": best["reason"],
        "profile": profile
    }

def predict_dragons_gold(profile: str):
    options = [
        {
            "path": "steal_silently",
            "survival_chance": 0.9,
            "score_range": (6, 9),
            "risk": 0.3,
            "reason": "Tu voles sans réveiller le dragon, discret et rentable."
        },
        {
            "path": "fight_dragon",
            "survival_chance": 0.35,
            "score_range": (4, 10),
            "risk": 0.9,
            "reason": "Combat direct, très risqué mais glorieux si tu réussis."
        },
        {
            "path": "negotiate",
            "survival_chance": 0.75,
            "score_range": (5, 8),
            "risk": 0.5,
            "reason": "Tu joues la diplomatie, bon équilibre entre risque et gain."
        }
    ]
    best = max(options, key=lambda o: compute_option_score(o, profile))
    score = random.randint(*best["score_range"])
    return {
        "game": "dragons_gold",
        "best_path": best["path"],
        "survival_chance": round(best["survival_chance"] * 100, 1),
        "predicted_score": score,
        "reason": best["reason"],
        "profile": profile
    }

def predict_royal_feast(profile: str):
    options = [
        {
            "path": "golden_door",
            "survival_chance": 0.89,
            "score_range": (7, 10),
            "risk": 0.3,
            "reason": "Tu choisis la voie royale, protégée et avantageuse."
        },
        {
            "path": "secret_passage",
            "survival_chance": 0.7,
            "score_range": (5, 9),
            "risk": 0.5,
            "reason": "Chemin discret, bon compromis entre risque et récompense."
        },
        {
            "path": "front_gate",
            "survival_chance": 0.5,
            "score_range": (3, 9),
            "risk": 0.7,
            "reason": "Tu arrives par l’entrée principale, visible mais assumé."
        }
    ]
    best = max(options, key=lambda o: compute_option_score(o, profile))
    score = random.randint(*best["score_range"])
    return {
        "game": "royal_feast",
        "best_path": best["path"],
        "survival_chance": round(best["survival_chance"] * 100, 1),
        "predicted_score": score,
        "reason": best["reason"],
        "profile": profile
    }

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
    # On limite la taille des logs
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

@app.get("/ui", response_class=HTMLResponse)
async def ui_page():
    with open("static/ui.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(key: str = Query(None)):
    if key != ADMIN_KEY:
        return HTMLResponse("<h1>Accès refusé</h1><p>Clé invalide.</p>", status_code=403)
    with open("static/admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/admin/data")
async def admin_data(key: str = Query(None)):
    if key != ADMIN_KEY:
        return JSONResponse({"error": "Clé invalide"}, status_code=403)
    # Stats simples
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
        "logs": game_logs[-50:]  # derniers 50
    })
