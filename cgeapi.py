import asyncio
import time
import a2s
from fastapi import FastAPI
from contextlib import asynccontextmanager

SERVER_IP = "169.150.249.133"
SERVER_PORT = 22912

LATEST_SERVER_INFO = {
    "status": "initializing",
    "server_name": "Loading...",
    "map": "Unknown",
    "players": 0,
    "max_players": 0,
    "game": "Unknown",
    "version": "Unknown",
    "password_protected": False,
    "players_list": [],
    "last_updated": 0
}

async def poll_game_server():
    global LATEST_SERVER_INFO
    
    while True:
        try:
            info = await a2s.ainfo((SERVER_IP, SERVER_PORT), timeout=3.0)
            
            players_list = []
            try:
                players = await a2s.aplayers((SERVER_IP, SERVER_PORT), timeout=2.0)
                if players:
                    players_list = [
                        {"name": p.name or "Unknown", "score": p.score, "duration": p.duration}
                        for p in players
                    ]
            except Exception:
                pass  

            LATEST_SERVER_INFO = {
                "status": "online",
                "server_name": getattr(info, "server_name", "Unknown"),
                "map": getattr(info, "map_name", "Unknown"),
                "players": getattr(info, "player_count", 0),
                "max_players": getattr(info, "max_players", 0),
                "game": getattr(info, "game", "Unknown"),
                "version": getattr(info, "version", "Unknown"),
                "password_protected": getattr(info, "password_protected", False),
                "players_list": players_list,
                "last_updated": time.time()
            }
        except Exception:
            LATEST_SERVER_INFO["status"] = "locked_or_changing_map"
        
        await asyncio.sleep(5)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(poll_game_server())
    yield
    task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/serverinfo")
async def get_server_info():
    return LATEST_SERVER_INFO