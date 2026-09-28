import asyncio
import time
import a2s
from fastapi import FastAPI

app = FastAPI()

SERVER_IP = "169.150.249.133"
SERVER_PORT = 22912  

CACHE = {
    "data": None,
    "last_updated": 0
}
CACHE_TTL = 10  

@app.get("/serverinfo")
async def get_server_info():
    now = time.time()
    
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

        response_data = {
            "status": "online",
            "server_name": getattr(info, "server_name", "Unknown"),
            "map": getattr(info, "map_name", "Unknown"),
            "players": getattr(info, "player_count", 0),
            "max_players": getattr(info, "max_players", 0),
            "game": getattr(info, "game", "Unknown"),
            "version": getattr(info, "version", "Unknown"),
            "password_protected": getattr(info, "password_protected", False),
            "players_list": players_list
        }
        
        CACHE["data"] = response_data
        CACHE["last_updated"] = now
        return response_data

    except Exception as e:
        # If query fails but we have fresh cached data (within TTL), serve cached data
        if CACHE["data"] and (now - CACHE["last_updated"]) < CACHE_TTL:
            cached_res = CACHE["data"].copy()
            cached_res["status"] = "updating"
            return cached_res

        return {
            "status": "unreachable",
            "server_name": "Server Unreachable",
            "map": "Unknown",
            "players": 0,
            "max_players": 0,
            "game": "Unknown",
            "version": "Unknown",
            "password_protected": True,  # Assume protected or restarting
            "players_list": []
        }