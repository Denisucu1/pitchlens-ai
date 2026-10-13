import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "PitchLens AI - Premier League Broadcasting Copilot"
    VERSION: str = "1.0.0"
    
    # Azure OpenAI & Microsoft Foundry Configuration
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    
    # Direct OpenAI fallback (if user has standard key)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Simulation settings
    SIMULATION_TICK_SECONDS: float = float(os.getenv("SIMULATION_TICK_SECONDS", "1.5"))
    DEFAULT_MATCH_SPEED: float = 1.0  # Multiplier for simulation playback
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
