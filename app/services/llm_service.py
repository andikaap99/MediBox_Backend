import httpx
from app.core.config import QWEN_API_KEY, QWEN_API_URL

async def call_qwen(user_message: str, slot_context: str, rag_context: str, history: list[dict] = None) -> str:
    system_prompt = f"""Kamu adalah asisten kesehatan MediBox AI.
Tugasmu membantu pengguna mengetahui obat yang tersedia di kotak obat mereka berdasarkan gejala yang dirasakan.

Kondisi kotak obat pengguna saat ini:
{slot_context}

Pengetahuan obat yang relevan:
{rag_context}

Instruksi:
- Rekomendasikan obat hanya dari daftar yang TERSEDIA di atas.
- Jika tidak ada obat yang cocok atau semua kosong, sarankan ke dokter.
- Jawab dalam Bahasa Indonesia, singkat dan jelas.
- Jangan mengarang obat di luar daftar yang tersedia."""

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        for entry in history:
            messages.append({"role": "user", "content": entry["user_message"]})
            messages.append({"role": "assistant", "content": entry["bot_response"]})

    messages.append({"role": "user", "content": user_message})

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            QWEN_API_URL,
            headers={
                "Authorization": f"Bearer {QWEN_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30.0
        )
        data = response.json()

        if "error" in data:
            raise Exception(f"Qwen API error: {data['error'].get('message', 'Unknown error')}")

        return data["choices"][0]["message"]["content"]