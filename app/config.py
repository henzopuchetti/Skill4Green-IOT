import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
    GEMINI_BASE = os.getenv("GEMINI_BASE", "https://generativelanguage.googleapis.com").rstrip("/")

    # Negócio
    EMISSION_FACTOR = float(os.getenv("EMISSION_FACTOR", "0.084"))
    TARIFF_KWH = float(os.getenv("TARIFF_KWH", "0.95"))

        # YOLO
    YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolo11n.pt")  # use seu 'best.pt' se tiver
    SSIM_THRESHOLD = float(os.getenv("SSIM_THRESHOLD", "0.75"))
    YOLO_DELTA_MIN = int(os.getenv("YOLO_DELTA_MIN", "1"))        # diferença mínima de contagem


settings = Settings()
