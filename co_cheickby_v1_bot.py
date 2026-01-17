from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/start")
def start(game: str):
    return JSONResponse(content={"message": f"Bienvenue dans {game}! Prépare-toi à jouer."})

@app.get("/action")
def action(game: str):
    return JSONResponse(content={
        "game": game,
        "score": 6,
        "survived": True
    })

@app.post("/")
async def poe_handler(request: Request):
    data = await request.json()
    message = data.get("message", "").lower()

    if "start" in message:
        game = message.replace("start", "").strip().replace(" ", "_")
        return JSONResponse(content={"message": f"Bienvenue dans {game}! Prépare-toi à jouer."})

    elif "action" in message:
        game = message.replace("action", "").strip().replace(" ", "_")
        return JSONResponse(content={"game": game, "score": 6, "survived": True})

    return JSONResponse(content={"message": "Commande inconnue. Utilise 'start [jeu]' ou 'action [jeu]'."})
