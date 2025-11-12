from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.config import settings
from app.gemini_client import gemini_chat
from app.prompts import sys_prompt, build_recommendations_prompt, build_motivation_prompt
from app.cv import compare_before_after
from fastapi.middleware.cors import CORSMiddleware
from app.cv_yolo import yolo_infer
from app.config import settings


app = FastAPI(title="Skill4Green AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======== Schemas ========

class RecentTask(BaseModel):
    task_code: str
    count: int

class Goals(BaseModel):
    dept_kwh_reduction_pct: Optional[float] = None

class UserInfo(BaseModel):
    id: str
    name: Optional[str] = None

class UserSummary(BaseModel):
    user: UserInfo
    department: Optional[str] = None
    skills: Optional[List[str]] = None
    recent_tasks: Optional[List[RecentTask]] = None
    goals: Optional[Goals] = None
    extra: Optional[Dict[str, Any]] = None

class RecommendationsReq(BaseModel):
    user_summary: UserSummary
    max_items: int = Field(default=4, ge=1, le=8)

class MotivationReq(BaseModel):
    kwh: float = 0.0
    co2: Optional[float] = None
    cost: Optional[float] = None
    name: Optional[str] = None

# ======== Health ========
@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.GEMINI_MODEL}

# ======== IA: Recomendações ========
@app.post("/ai/recommendations")
async def recommendations(req: RecommendationsReq):
    messages = [
        {"role": "system", "content": sys_prompt()},
        {"role": "user", "content": build_recommendations_prompt(req.user_summary.model_dump(), req.max_items)}
    ]

    text = await gemini_chat(messages, temperature=0.2, max_tokens=300)

    if not text.strip():
        fallback = [
            "Automação de desligamento fora do expediente",
            "Troca progressiva para LED nas áreas de maior uso",
            "Boas práticas de TI Verde (monitores/impressoras em modo economia)",
            "Auditoria de modo repouso por setor"
        ]
        return {"items": fallback[:req.max_items]}

    items: List[str] = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•* ").strip()
        if line:
            items.append(line)
    return {"items": items[:req.max_items]}

# ======== IA: Motivação ========
@app.post("/ai/motivation")
async def motivation(req: MotivationReq):
    kwh = float(req.kwh or 0.0)
    co2 = req.co2 if req.co2 is not None else kwh * settings.EMISSION_FACTOR
    cost = req.cost if req.cost is not None else kwh * settings.TARIFF_KWH
    data = {"kwh": kwh, "co2": co2, "cost": cost, "name": req.name}

    messages = [
        {"role": "system", "content": sys_prompt()},
        {"role": "user", "content": build_motivation_prompt(data)}
    ]
    text = await gemini_chat(messages, temperature=0.3, max_tokens=120)

    if not text.strip():
        houses = int(max(kwh / 30.0, 0))
        if houses > 0:
            msg = (
                f"Parabéns{', ' + (req.name or '') if req.name else ''}! "
                f"Você economizou {kwh:.2f} kWh (≈ {houses} casa(s)/dia), "
                f"evitou {co2:.2f} kg de CO₂ e poupou R$ {cost:.2f}. Siga nesse ritmo!"
            )
        else:
            msg = (
                f"Ótimo trabalho{', ' + (req.name or '') if req.name else ''}! "
                f"Economia de {kwh:.2f} kWh, {co2:.2f} kg de CO₂ e R$ {cost:.2f}. "
                f"Vamos buscar a próxima meta!"
            )
        return {"message": msg, "computed": data}

    return {"message": text.strip(), "computed": data}

# ======== CV: comparação antes/depois ========
@app.post("/cv/compare")
async def cv_compare(before: UploadFile = File(...), after: UploadFile = File(...)):
    result = await compare_before_after(before, after)
    return result

@app.post("/cv/verify")
async def cv_verify(
    before: UploadFile = File(...),
    after: UploadFile = File(...)
):
    """
    Verifica se houve mudança relevante entre 'antes' e 'depois',
    combinando SSIM (estrutura) + YOLO (objetos),
    e retorna mensagem explícita de confirmação.
    """
    # 1) SSIM
    ssim_result = await compare_before_after(before, after)
    ssim_score = float(ssim_result["ssim"])
    ssim_changed = ssim_score < settings.SSIM_THRESHOLD

    # re-leia os bytes (o compare_before_after já consumiu)
    before.file.seek(0)
    after.file.seek(0)
    b_bytes = await before.read()
    a_bytes = await after.read()

    # 2) YOLO (pode falhar se ultralytics/torch não estiverem OK)
    yolo_ok = True
    yolo_before = {}
    yolo_after = {}
    try:
        yolo_before = yolo_infer(b_bytes)
        yolo_after  = yolo_infer(a_bytes)
    except Exception as e:
        yolo_ok = False
        print("[yolo] erro:", e)

    # 3) Heurística de delta em classes (só se YOLO rodou)
    changed_classes = {}
    yolo_changed = False
    if yolo_ok:
        cb = yolo_before.get("counts_by_class", {})
        ca = yolo_after.get("counts_by_class", {})
        all_classes = set(cb.keys()) | set(ca.keys())
        for cls in all_classes:
            vb = cb.get(cls, 0)
            va = ca.get(cls, 0)
            if abs(va - vb) >= settings.YOLO_DELTA_MIN:
                changed_classes[cls] = {"before": vb, "after": va}
        yolo_changed = len(changed_classes) > 0

    # 4) Veredito + mensagem explícita na API
    changed = (ssim_changed or yolo_changed)
    verdict = "CHANGED" if changed else "SMALL_CHANGE"

    if changed:
        message = "Depois da análise, foi detectada uma mudança e entendemos que a tarefa foi realizada."
        approved = True
    else:
        message = "Depois da análise, não identificamos mudança suficiente para confirmar a execução da tarefa."
        approved = False

    return {
        "verdict": verdict,
        "approved": approved,   # bool direto para o seu backend Java decidir fluxo
        "message": message,     # mensagem explícita
        "ssim": {
            "score": ssim_score,
            "threshold": settings.SSIM_THRESHOLD,
            "changed": ssim_changed
        },
        "yolo": {
            "enabled": yolo_ok,
            "delta_min": settings.YOLO_DELTA_MIN,
            "before": yolo_before,
            "after": yolo_after,
            "changed_classes": changed_classes,
            "changed": yolo_changed
        }
    }
