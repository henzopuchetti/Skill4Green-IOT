def sys_prompt():
    return (
        "Você é o módulo de IA do Skill4Green. Gere recomendações e mensagens "
        "curtas, específicas, acionáveis, alinhadas a sustentabilidade corporativa."
    )

def build_recommendations_prompt(user_summary: dict, max_items: int = 4) -> str:
    """
    user_summary (exemplo):
    {
      "user": {"id":"...", "name":"Ana"},
      "department":"TI",
      "skills":["eletrica_basica","automacao","interesse_aprender"],
      "recent_tasks":[
        {"task_code":"AC_OFF_AFTER_HOURS","count":5},
        {"task_code":"LED_REPLACE","count":2}
      ],
      "goals":{"dept_kwh_reduction_pct":5}
    }
    """
    return f"""
Contexto do usuário (JSON):
{user_summary}

Tarefa:
- Gere até {max_items} recomendações curtas de trilhas/ações (bullet points).
- Priorize o que gera maior impacto kWh/CO₂ para o departamento.
- Use linguagem simples. Cada item em 1 linha.

Formato de saída:
- Uma lista de itens, um por linha, sem numeração.
""".strip()

def build_motivation_prompt(last_saved: dict) -> str:
    """
    last_saved (exemplo): {"kwh":1.2,"co2":0.10,"cost":1.14,"name":"Ana"}
    """
    name = last_saved.get("name") or "Você"
    kwh = float(last_saved.get("kwh") or 0.0)
    co2 = float(last_saved.get("co2") or 0.0)
    cost = float(last_saved.get("cost") or 0.0)
    houses = int(max(kwh / 30.0, 0))  # aproximação simples

    return f"""
Dados:
- Nome: {name}
- Economia: {kwh:.2f} kWh | {co2:.2f} kg CO₂ | R$ {cost:.2f}
- Equivalência: {houses} casa(s)/dia aprox.

Tarefa:
- Escreva 1 mensagem motivacional curta (1-2 frases), positiva, concreta.
- Cite ao menos uma métrica (kWh, CO₂, ou R$).
- Se houses > 0, use a equivalência.
- Sem emojis.

Retorne só a mensagem.
""".strip()
