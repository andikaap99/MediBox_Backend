from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_device(user_id: str) -> dict | None:
    response = supabase.table("devices") \
        .select("id, mac_address, device_name, created_at") \
        .eq("user_id", user_id) \
        .execute()

    if response.data:
        return response.data[0]

    return None


def upsert_device(user_id: str, mac_address: str, device_name: str = "") -> dict:
    mac_normalized = mac_address.upper().strip()

    existing = supabase.table("devices") \
        .select("id") \
        .eq("user_id", user_id) \
        .execute()

    if existing.data:
        supabase.table("devices") \
            .update({
                "mac_address": mac_normalized,
                "device_name": device_name
            }) \
            .eq("user_id", user_id) \
            .execute()

        updated = supabase.table("devices") \
            .select("id, mac_address, device_name, created_at") \
            .eq("user_id", user_id) \
            .execute()

        return updated.data[0]
    else:
        result = supabase.table("devices").insert({
            "user_id": user_id,
            "mac_address": mac_normalized,
            "device_name": device_name
        }).execute()

        return result.data[0]


def delete_device(user_id: str):
    supabase.table("devices") \
        .delete() \
        .eq("user_id", user_id) \
        .execute()


def get_user_id_by_mac(mac_address: str) -> str | None:
    mac_normalized = mac_address.upper().strip()

    response = supabase.table("devices") \
        .select("user_id") \
        .eq("mac_address", mac_normalized) \
        .execute()

    if response.data:
        return response.data[0]["user_id"]

    return None
