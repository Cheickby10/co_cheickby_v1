from fastapi import FastAPI
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
