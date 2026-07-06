from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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