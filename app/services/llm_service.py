import httpx
from app.core.config import QWEN_API_KEY, QWEN_API_URL

async def call_qwen(user_message: str, slot_context: str, rag_context: str) -> str:
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

    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
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
        
        return data["choices"][0]["message"]["content"]