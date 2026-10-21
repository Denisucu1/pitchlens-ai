import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router as match_router
from app.api.websocket import ws_router, match_simulation_loop
from app.api.audio import audio_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start match simulation loop in background
    sim_task = asyncio.create_task(match_simulation_loop())
    print("[PitchLens AI] Match simulation engine started.")
    yield
    # Shutdown: Cancel background simulation loop
    sim_task.cancel()
    try:
        await sim_task
    except asyncio.CancelledError:
        pass
    print("[PitchLens AI] Match simulation engine stopped.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Explainable Match Intelligence & Broadcasting Copilot for Premier League synthetic data.",
    lifespan=lifespan
)

# Enable CORS for local frontend development and production hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API and WebSocket routes
app.include_router(match_router)
app.include_router(ws_router)
app.include_router(audio_router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
