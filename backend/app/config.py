import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "PitchLens AI - Premier League Broadcasting Copilot"
    VERSION: str = "1.0.0"
    
    # Azure OpenAI & Microsoft Foundry Configuration
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "Phi-4-mini-instruct")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    
    # Direct OpenAI fallback
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    
    # Calibrated simulation pacing: 2.8s gives natural breathing room and allows audio commentary to complete
    SIMULATION_TICK_SECONDS: float = float(os.getenv("SIMULATION_TICK_SECONDS", "2.8"))
    DEFAULT_MATCH_SPEED: float = 1.0
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
