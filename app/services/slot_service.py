from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_chat_history(user_id: str, user_message: str, bot_response: str):
    supabase.table("chat_sessions").insert({
        "user_id": user_id,
        "user_message": user_message,
        "bot_response": bot_response
    }).execute()


def get_chat_history(user_id: str, limit: int = 10) -> list[dict]:
    response = supabase.table("chat_sessions") \
        .select("user_message, bot_response") \
        .eq("user_id", user_id) \
        .order("id", desc=True) \
        .limit(limit) \
        .execute()

    rows = response.data or []
    return list(reversed(rows))


def get_slot_context(user_id: str) -> str:
    response = supabase.table("slots") \
        .select("slot_label, medicine_name, is_filled") \
        .eq("user_id", user_id) \
        .execute()

    slots = response.data
    if not slots:

        return "Tidak ada data slot obat."

    lines = []
    for slot in slots:
        status = "TERSEDIA" if slot["is_filled"] else "KOSONG"
        lines.append(f"- Slot {slot['slot_label']}: {slot['medicine_name']} ({status})")

    return "\n".join(lines)


def get_all_slots(user_id: str) -> list[dict]:
    response = supabase.table("slots") \
        .select("id, slot_label, medicine_name, is_filled") \
        .eq("user_id", user_id) \
        .order("slot_label") \
        .execute()

    return response.data or []


def add_slot(user_id: str, slot_label: str, medicine_name: str = "") -> dict:
    existing = supabase.table("slots") \
        .select("id") \
        .eq("user_id", user_id) \
        .eq("slot_label", slot_label) \
        .execute()

    if existing.data:
        raise ValueError(f"Slot {slot_label} sudah ada untuk user ini")

    result = supabase.table("slots").insert({
        "user_id": user_id,
        "slot_label": slot_label,
        "medicine_name": medicine_name,
        "is_filled": False
    }).execute()

    return result.data[0]


def update_slot_config(slot_id: str, medicine_name: str):
    supabase.table("slots") \
        .update({"medicine_name": medicine_name}) \
        .eq("id", slot_id) \
        .execute()