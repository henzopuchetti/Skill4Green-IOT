from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.config import settings
from app.groq_client import groq_chat
from app.prompts import sys_prompt
from app.cv import compare_before_after
from fastapi.middleware.cors import CORSMiddleware
from app.cv_yolo import yolo_infer

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
    task_code: str                      # código da tarefa escolhida
    executions: int = 1                 # quantas vezes essa tarefa foi feita
    name: Optional[str] = None          # nome do usuário (opcional)

    # Se vierem, sobrescrevem o cálculo automático
    kwh: Optional[float] = None
    co2: Optional[float] = None
    cost: Optional[float] = None


# ======== Health ========


@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.GROQ_MODEL}


# ======== IA: Recomendações ========


@app.post("/ai/recommendations")
async def recommendations(req: RecommendationsReq):
    """
    Gera recomendações de tarefas sustentáveis adaptadas ao setor/perfil do usuário.
    Usa o LLM apenas para texto; cálculo de impacto fica no backend.
    """
    sector = req.user_summary.department or "não informado"
    skills = ", ".join(req.user_summary.skills or [])
    recent_tasks_str = ", ".join(
        [task.task_code for task in (req.user_summary.recent_tasks or [])]
    )
    goals_pct = (
        req.user_summary.goals.dept_kwh_reduction_pct
        if req.user_summary.goals
        and req.user_summary.goals.dept_kwh_reduction_pct is not None
        else None
    )

    prompt = f"""
Você é o módulo de IA do Skill4Green.

Usuário:
- Setor: {sector}
- Skills: {skills or "não informado"}
- Tarefas recentes: {recent_tasks_str or "nenhuma informada"}
- Meta de redução de energia do setor: {goals_pct if goals_pct is not None else "não informada"} (%).

Tarefa:
- Gere de 3 a 5 tarefas de sustentabilidade ESPECÍFICAS para o setor de {sector}.
- Cada tarefa deve ser prática, executável em ambiente corporativo e relevante para esse setor.
- Adapte o tipo de ação ao perfil (skills) do usuário.
- Foque em ações com impacto real em consumo de energia e emissões (kWh / CO₂),
  mesmo que a estimativa numérica seja feita depois pelo backend.

Formato de saída:
- Uma tarefa por linha, sem numeração explícita.
- Não escreva explicações longas; foque na ação em si.
""".strip()

    messages = [
        {"role": "system", "content": sys_prompt()},
        {"role": "user", "content": prompt},
    ]

    text = await groq_chat(messages, temperature=0.5, max_tokens=500)

    if not text or not text.strip():
        text = "Nenhuma recomendação adequada foi gerada. Por favor, tente novamente."

    tasks = [line.strip("-• ").strip() for line in text.splitlines() if line.strip()]

    return {"items": tasks[:req.max_items]}


@app.post("/ai/recommendations/refresh")
async def refresh_recommendations(req: RecommendationsReq):
    """
    Gera um novo conjunto de tarefas sustentáveis para o mesmo contexto,
    útil para o botão de "gerar novas sugestões".
    """
    sector = req.user_summary.department or "não informado"
    skills = ", ".join(req.user_summary.skills or [])
    recent_tasks_str = ", ".join(
        [task.task_code for task in (req.user_summary.recent_tasks or [])]
    )
    goals_pct = (
        req.user_summary.goals.dept_kwh_reduction_pct
        if req.user_summary.goals
        and req.user_summary.goals.dept_kwh_reduction_pct is not None
        else None
    )

    prompt = f"""
Você é o módulo de IA do Skill4Green.

Usuário:
- Setor: {sector}
- Skills: {skills or "não informado"}
- Tarefas recentes: {recent_tasks_str or "nenhuma informada"}
- Meta de redução de energia do setor: {goals_pct if goals_pct is not None else "não informada"} (%).

Tarefa:
- Gere um NOVO conjunto de 3 a 5 tarefas de sustentabilidade diferentes das anteriores.
- Todas devem ser específicas para o setor de {sector} e alinhadas às skills do usuário.
- Foque em ações com impacto em economia de energia e emissões.

Formato de saída:
- Uma tarefa por linha, sem numeração explícita.
- Não repita exatamente as mesmas tarefas já sugeridas.
""".strip()

    messages = [
        {"role": "system", "content": sys_prompt()},
        {"role": "user", "content": prompt},
    ]

    text = await groq_chat(messages, temperature=0.6, max_tokens=500)

    if not text or not text.strip():
        text = "Nenhuma nova recomendação adequada foi gerada. Por favor, tente novamente."

    tasks = [line.strip("-• ").strip() for line in text.splitlines() if line.strip()]

    return {"items": tasks[:req.max_items]}


# ======== Tabela de impacto por tarefa (base de cálculo) ========

TASK_IMPACT = {
    # TI
    "AC_OFF_AFTER_HOURS": {"kwh_per_execution": 1.2},
    "LED_REPLACE": {"kwh_per_execution": 0.5},
    "MONITOR_SLEEP_POLICY": {"kwh_per_execution": 0.3},
    "SERVER_ROOM_TEMP_OPTIMIZE": {"kwh_per_execution": 3.0},

    # RH (exemplos, ajuste depois conforme seu domínio)
    "AWARENESS_CAMPAIGN": {"kwh_per_execution": 0.8},
    "GREEN_WORKSHOPS": {"kwh_per_execution": 1.5},
}


# ======== IA: Motivação ========


@app.post("/ai/motivation")
async def motivation(req: MotivationReq):
    """
    Gera mensagem motivacional e calcula impacto (kWh, CO₂, R$)
    de forma automática com base na tarefa escolhida.

    Regras:
    - Sempre exige task_code.
    - executions = quantas vezes a tarefa foi feita (default 1).
    - Se kwh/co2/cost vierem preenchidos, eles sobrescrevem o cálculo automático.
    """

    # 1) Pega o impacto base da tarefa
    impact = TASK_IMPACT.get(req.task_code, {})
    kwh_per_exec = float(impact.get("kwh_per_execution", 0.0))

    # 2) Calcula kWh total pela quantidade de execuções
    base_kwh = kwh_per_exec * max(req.executions, 1)

    # 3) Decide o kWh final
    if req.kwh is not None and req.kwh > 0:
        kwh = float(req.kwh)
    else:
        kwh = base_kwh

    # 4) CO₂ (kg)
    if req.co2 is not None:
        co2 = float(req.co2)
    else:
        co2 = kwh * settings.EMISSION_FACTOR  # kg CO₂ por kWh

    # 5) Custo (R$)
    if req.cost is not None:
        cost = float(req.cost)
    else:
        cost = kwh * settings.TARIFF_KWH  # R$/kWh

    # 6) Mensagem motivacional
    name_part = f", {req.name}" if req.name else ""
    message = (
        f"Parabéns{name_part}! "
        f"Com a tarefa '{req.task_code}' realizada {req.executions} vez(es), "
        f"você economizou aproximadamente {kwh:.2f} kWh, evitou {co2:.2f} kg de CO₂ "
        f"e poupou cerca de R$ {cost:.2f}."
    )

    return {
        "message": message,
        "computed": {
            "task_code": req.task_code,
            "executions": req.executions,
            "kwh": kwh,
            "co2": co2,
            "cost": cost,
        },
    }


# ======== CV: Verificar SSIM + YOLO ========


@app.post("/cv/verify")
async def cv_verify(before: UploadFile = File(...), after: UploadFile = File(...)):
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
        yolo_after = yolo_infer(a_bytes)
    except Exception as e:
        yolo_ok = False
        print("[yolo] erro:", e)

    # 3) Heurística de delta em classes (só se YOLO rodou)
    changed_classes: Dict[str, Dict[str, int]] = {}
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
    changed = ssim_changed or yolo_changed
    verdict = "CHANGED" if changed else "SMALL_CHANGE"

    if changed:
        message = (
            "Depois da análise, foi detectada uma mudança e entendemos "
            "que a tarefa foi realizada."
        )
        approved = True
    else:
        message = (
            "Depois da análise, não identificamos mudança suficiente para "
            "confirmar a execução da tarefa."
        )
        approved = False

    return {
        "verdict": verdict,
        "approved": approved,  # bool direto para o backend Java decidir fluxo
        "message": message,    # mensagem explícita
        "ssim": {
            "score": ssim_score,
            "threshold": settings.SSIM_THRESHOLD,
            "changed": ssim_changed,
        },
        "yolo": {
            "enabled": yolo_ok,
            "delta_min": settings.YOLO_DELTA_MIN,
            "before": yolo_before,
            "after": yolo_after,
            "changed_classes": changed_classes,
            "changed": yolo_changed,
        },
    }
