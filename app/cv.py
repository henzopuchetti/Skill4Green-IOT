from fastapi import UploadFile
from skimage.metrics import structural_similarity as ssim
import numpy as np
import cv2


def _to_gray_512(img_bytes: bytes):
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Imagem inválida")
    img = cv2.resize(img, (512, 512))
    return img


async def compare_before_after(before: UploadFile, after: UploadFile):
    b = await before.read()
    a = await after.read()
    imgB = _to_gray_512(b)
    imgA = _to_gray_512(a)
    score, _ = ssim(imgB, imgA, full=True)
    verdict = "CHANGED" if score < 0.75 else "SMALL_CHANGE"
    return {"ssim": float(score), "verdict": verdict}
