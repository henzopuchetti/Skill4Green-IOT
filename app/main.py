from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.config import settings
from app.ollama_client import ollama_chat
from app.prompts import sys_prompt, build_recommendations_prompt, build_motivation_prompt
from app.cv import compare_before_after
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Skill4Green AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ajuste se quiser restringir
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
    extra: Optional[Dict[str, Any]] = None  # livre

class RecommendationsReq(BaseModel):
    user_summary: UserSummary
    max_items: int = Field(default=4, ge=1, le=8)

class MotivationReq(BaseModel):
    kwh: float = 0.0
    co2: Optional[float] = None   # pode vir null
    cost: Optional[float] = None  # pode vir null
    name: Optional[str] = None

# ======== Health ========
@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.OLLAMA_MODEL}

# ======== IA: Recomendações ========
@app.post("/ai/recommendations")
async def recommendations(req: RecommendationsReq):
    messages = [
        {"role": "system", "content": sys_prompt()},
        {"role": "user", "content": build_recommendations_prompt(req.user_summary.model_dump(), req.max_items)}
    ]

    text = await ollama_chat(messages, temperature=0.2, max_tokens=300)

    # Se Ollama estiver fora, usa fallback para não quebrar
    if not text.strip():
        fallback = [
            "Automação de desligamento fora do expediente",
            "Troca progressiva para LED nas áreas de maior uso",
            "Boas práticas de TI Verde (monitores/impressoras em modo economia)",
            "Auditoria de modo repouso por setor"
        ]
        return {"items": fallback[:req.max_items]}

    # Parse simples: cada linha vira um item; limpa marcadores
    items: List[str] = []
    for line in text.splitlines():
        line = line.strip().lstrip("-•* ").strip()
        if line:
            items.append(line)
    return {"items": items[:req.max_items]}

# ======== IA: Motivação ========
@app.post("/ai/motivation")
async def motivation(req: MotivationReq):
    # Mantém 0.0 válido (não trata 0 como "falsy")
    kwh = float(req.kwh or 0.0)
    co2 = req.co2 if req.co2 is not None else kwh * settings.EMISSION_FACTOR
    cost = req.cost if req.cost is not None else kwh * settings.TARIFF_KWH
    data = {"kwh": kwh, "co2": co2, "cost": cost, "name": req.name}

    messages = [
        {"role": "system", "content": sys_prompt()},
        {"role": "user", "content": build_motivation_prompt(data)}
    ]
    text = await ollama_chat(messages, temperature=0.3, max_tokens=120)

    # Fallback quando Ollama não responde
    if not text.strip():
        houses = int(max(kwh / 30.0, 0))
        if houses > 0:
            msg = (
                f"Parabéns{', ' + req.name if req.name else ''}! "
                f"Você economizou {kwh:.2f} kWh (≈ {houses} casa(s)/dia), "
                f"evitou {co2:.2f} kg de CO₂ e poupou R$ {cost:.2f}. Siga nesse ritmo!"
            )
        else:
            msg = (
                f"Ótimo trabalho{', ' + req.name if req.name else ''}! "
                f"Economia de {kwh:.2f} kWh, {co2:.2f} kg de CO₂ e R$ {cost:.2f}. "
                f"Vamos buscar a próxima meta!"
            )
        return {"message": msg, "computed": data}

    return {"message": text.strip(), "computed": data}

# ======== CV: comparação antes/depois (opcional) ========
@app.post("/cv/compare")
async def cv_compare(before: UploadFile = File(...), after: UploadFile = File(...)):
    result = await compare_before_after(before, after)
    return result

# (Opcional) YOLO:
# from ultralytics import YOLO
# model = YOLO("best.pt")
# @app.post("/cv/yolo/lamp")
# async def yolo_lamp(file: UploadFile = File(...)):
#     img = await file.read()
#     # inferência e retorno de confiança
#     return {"ok": True}
