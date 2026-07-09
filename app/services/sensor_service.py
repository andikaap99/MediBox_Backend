from datetime import datetime, timezone
from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def update_slot_from_sensor(user_id: str, slot_label: str, is_filled: bool):
    existing = supabase.table("slots") \
        .select("id") \
        .eq("user_id", user_id) \
        .eq("slot_label", slot_label) \
        .execute()

    if existing.data:
        supabase.table("slots") \
            .update({"is_filled": is_filled}) \
            .eq("user_id", user_id) \
            .eq("slot_label", slot_label) \
            .execute()
    else:
        supabase.table("slots") \
            .insert({
                "user_id": user_id,
                "slot_label": slot_label,
                "medicine_name": "",
                "is_filled": is_filled
            }) \
            .execute()

    supabase.table("slot_history").insert({
        "user_id": user_id,
        "slot_label": slot_label,
        "is_filled": is_filled,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }).execute()
