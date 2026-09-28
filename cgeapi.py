import asyncio
import a2s
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVER_IP = "169.150.249.133"
SERVER_PORT = 22912
QUERY_TIMEOUT = 3.0


@app.get("/serverinfo")
async def get_server_info():
    try:
        # 1. Fetch server info
        info = await a2s.ainfo((SERVER_IP, SERVER_PORT), timeout=QUERY_TIMEOUT)
    except Exception:
        raise HTTPException(status_code=504, detail="Server unreachable")

    is_protected = getattr(info, "password_protected", False)

    players_list = []
    try:
        players = await a2s.aplayers((SERVER_IP, SERVER_PORT), timeout=QUERY_TIMEOUT)
        if players:
            players_list = [
                {
                    "name": p.name or "Unknown",
                    "score": p.score,
                    "duration": p.duration,
                }
                for p in players
            ]
    except Exception:
        pass

    return {
        "server_name": getattr(info, "server_name", "Unknown"),
        "map": getattr(info, "map_name", "Unknown"),
        "players": getattr(info, "player_count", 0),
        "max_players": getattr(info, "max_players", 0),
        "game": getattr(info, "game", "Unknown"),
        "version": getattr(info, "version", "Unknown"),
        "password_protected": is_protected,
        "status": "Private Match" if is_protected else "Public",
        "players_list": players_list,
    }