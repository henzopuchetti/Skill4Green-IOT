import httpx
from app.config import settings

def _to_gemini_contents(messages):
    """
    Converte mensagens [{role, content}] para o formato do Gemini.
    Aqui, colamos tudo em um único conteúdo de usuário para simplificar.
    """
    joined = []
    for m in messages:
        role = m.get("role", "user")
        prefix = "System: " if role == "system" else ("User: " if role == "user" else "Assistant: ")
        joined.append(prefix + str(m.get("content", "")))
    full = "\n\n".join(joined).strip()
    return {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": full}]
            }
        ]
    }

async def gemini_chat(messages, temperature=0.2, max_tokens=None) -> str:
    """
    Chama a REST API do Gemini 1.5 (generateContent).
    Retorna string vazia se houver erro (caller faz fallback).
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        print("[gemini] Faltando GEMINI_API_KEY no .env")
        return ""

    model = settings.GEMINI_MODEL
    url = f"{settings.GEMINI_BASE}/v1beta/models/{model}:generateContent?key={api_key}"

    payload = _to_gemini_contents(messages)
    payload["generationConfig"] = {
        "temperature": float(temperature)
    }
    if max_tokens is not None:
        # Para Gemini, o nome é maxOutputTokens
        payload["generationConfig"]["maxOutputTokens"] = int(max_tokens)

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            # Estrutura típica: candidates[0].content.parts[0].text
            candidates = data.get("candidates") or []
            if not candidates:
                return ""
            parts = (candidates[0].get("content") or {}).get("parts") or []
            if not parts:
                return ""
            text = parts[0].get("text") or ""
            return text
    except httpx.HTTPError as e:
        print(f"[gemini] HTTPError: {e}")
        return ""
    except Exception as e:
        print(f"[gemini] erro inesperado: {e}")
        return ""
