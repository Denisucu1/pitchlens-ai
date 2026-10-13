import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
from app.api.routes import global_orchestrator
from app.config import settings

ws_router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        dead_connections = set()
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)
        for dead in dead_connections:
            self.disconnect(dead)

manager = ConnectionManager()

# Background task runner for simulation loop
simulation_task = None

async def match_simulation_loop():
    """Continuously runs the match simulation and broadcasts ticks to connected clients."""
    while True:
        try:
            if not global_orchestrator.is_paused and len(manager.active_connections) > 0:
                payload = global_orchestrator.tick()
                # Pydantic v2 model_dump()
                data = payload.model_dump(mode="json")
                await manager.broadcast({"type": "MATCH_TICK", "data": data})
                
            sleep_duration = max(0.4, settings.SIMULATION_TICK_SECONDS / global_orchestrator.playback_speed)
            await asyncio.sleep(sleep_duration)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[Simulation Loop Error] {e}")
            await asyncio.sleep(1.0)

@ws_router.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Send initial state immediately upon connection
    if not global_orchestrator.current_payload:
        global_orchestrator.tick()
    await websocket.send_json({
        "type": "INITIAL_STATE",
        "data": global_orchestrator.current_payload.model_dump(mode="json")
    })
    
    try:
        while True:
            raw_text = await websocket.receive_text()
            cmd = json.loads(raw_text)
            action = cmd.get("action")
            
            if action == "PAUSE":
                global_orchestrator.is_paused = True
            elif action == "RESUME":
                global_orchestrator.is_paused = False
            elif action == "SET_SPEED":
                global_orchestrator.playback_speed = float(cmd.get("speed", 1.0))
            elif action == "SET_PLAYER_FOCUS":
                global_orchestrator.set_focused_player(cmd.get("player_id"))
            elif action == "SET_LANGUAGE":
                global_orchestrator.set_language(cmd.get("language"))
            elif action == "STEP":
                payload = global_orchestrator.tick()
                await websocket.send_json({
                    "type": "MATCH_TICK",
                    "data": payload.model_dump(mode="json")
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
