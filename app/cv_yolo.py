# app/cv_yolo.py
import io
from typing import Dict, Any, List
import numpy as np
import cv2

from app.config import settings

try:
    from ultralytics import YOLO
except Exception as e:
    YOLO = None
    print("[yolo] ultralytics indisponível:", e)

_model_cache = {"model": None, "names": {}}

def _ensure_model():
    if YOLO is None:
        raise RuntimeError("Ultralytics/YOLO não disponível. Verifique instalação.")
    if _model_cache["model"] is None:
        model_path = settings.YOLO_MODEL_PATH
        model = YOLO(model_path)  # carrega .pt (yolo11n.pt ou best.pt)
        names = model.model.names if hasattr(model, "model") else getattr(model, "names", {})
        _model_cache["model"] = model
        _model_cache["names"] = names or {}
    return _model_cache["model"], _model_cache["names"]

def _bytes_to_bgr(img_bytes: bytes) -> np.ndarray:
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Imagem inválida")
    return img

def yolo_infer(img_bytes: bytes) -> Dict[str, Any]:
    model, names = _ensure_model()
    img = _bytes_to_bgr(img_bytes)
    res = model.predict(img, imgsz=640, conf=0.25, verbose=False)
    # pega primeiro resultado
    r0 = res[0]
    det = r0.boxes
    classes: List[int] = det.cls.cpu().numpy().astype(int).tolist() if det is not None else []
    scores: List[float] = det.conf.cpu().numpy().astype(float).tolist() if det is not None else []
    # contagem por classe
    counts: Dict[str, int] = {}
    for c in classes:
        name = names.get(c, str(c))
        counts[name] = counts.get(name, 0) + 1
    return {
        "count_total": len(classes),
        "counts_by_class": counts,
        "scores_sample": scores[:5]
    }
