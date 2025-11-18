import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Groq (LLM)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
    GROQ_BASE = os.getenv("GROQ_BASE", "https://api.groq.com/openai/v1").rstrip("/")

    # Negócio
    EMISSION_FACTOR = float(os.getenv("EMISSION_FACTOR", "0.084"))
    TARIFF_KWH = float(os.getenv("TARIFF_KWH", "0.95"))

    # YOLO
    YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolo11n.pt")  # use seu 'best.pt' se tiver
    SSIM_THRESHOLD = float(os.getenv("SSIM_THRESHOLD", "0.75"))
    YOLO_DELTA_MIN = int(os.getenv("YOLO_DELTA_MIN", "1"))        # diferença mínima de contagem


settings = Settings()
