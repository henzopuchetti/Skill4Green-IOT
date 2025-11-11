import httpx
from app.config import settings

async def ollama_chat(messages, temperature=0.2, max_tokens=None) -> str:
    """
    Chama /api/chat do Ollama.
    messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
    Retorna string vazia em caso de indisponibilidade (caller faz fallback).
    """
    url = f"{settings.OLLAMA_BASE}/api/chat"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature}
    }
    if max_tokens is not None:
        payload["options"]["num_predict"] = max_tokens

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            return (data.get("message") or {}).get("content", "") or ""
    except httpx.HTTPError as e:
        # Loga e devolve fallback vazio (evita 500)
        print(f"[ollama] HTTPError: {e}")
        return ""
    except Exception as e:
        print(f"[ollama] erro inesperado: {e}")
        return ""
