import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434").rstrip("/")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    # parâmetros de negócio
    EMISSION_FACTOR = float(os.getenv("EMISSION_FACTOR", "0.084"))
    TARIFF_KWH = float(os.getenv("TARIFF_KWH", "0.95"))

settings = Settings()
