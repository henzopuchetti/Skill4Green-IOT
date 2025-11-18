import httpx
from app.config import settings


async def groq_chat(messages, temperature=0.2, max_tokens=None) -> str:
    """
    Client para a API de Chat Completions da Groq,
    usando modelo compatível com OpenAI (ex.: llama-3.3-70b-versatile).
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        print("[groq] Faltando GROQ_API_KEY no .env")
        return ""

    model = settings.GROQ_MODEL
    base = settings.GROQ_BASE.rstrip("/")
    # Ex: https://api.groq.com/openai/v1/chat/completions
    url = f"{base}/chat/completions"

    # Formato OpenAI/Groq:
    # [{ "role": "system" | "user" | "assistant", "content": "..." }]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": float(temperature),
    }
    if max_tokens is not None:
        payload["max_tokens"] = int(max_tokens)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print("[groq] URL:", url)
    print("[groq] Payload:", payload)

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
            r = await client.post(url, json=payload, headers=headers)
            if r.status_code >= 400:
                print("[groq] Status code:", r.status_code)
                print("[groq] Body erro:", r.text)
            r.raise_for_status()
            data = r.json()

            # Formato OpenAI/Groq:
            # choices[0].message.content
            choices = data.get("choices") or []
            if not choices:
                return ""
            msg = choices[0].get("message") or {}
            text = msg.get("content") or ""
            return text
    except httpx.HTTPError as e:
        print(f"[groq] HTTPError: {e}")
        return ""
    except Exception as e:
        print(f"[groq] erro inesperado:", e)
        return ""
