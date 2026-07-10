from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_device(user_id: str) -> dict | None:
    response = supabase.table("users") \
        .select("id, mac_address, device_name, created_at") \
        .eq("id", user_id) \
        .execute()

    if response.data and response.data[0].get("mac_address"):
        return response.data[0]

    return None


def upsert_device(user_id: str, mac_address: str, device_name: str = "") -> dict:
    mac_normalized = mac_address.upper().strip()

    supabase.table("users") \
        .update({
            "mac_address": mac_normalized,
            "device_name": device_name
        }) \
        .eq("id", user_id) \
        .execute()

    updated = supabase.table("users") \
        .select("id, mac_address, device_name, created_at") \
        .eq("id", user_id) \
        .execute()

    return updated.data[0]


def delete_device(user_id: str):
    supabase.table("users") \
        .update({"mac_address": None, "device_name": None}) \
        .eq("id", user_id) \
        .execute()


def get_device_by_mac(mac_address: str) -> dict | None:
    mac_normalized = mac_address.upper().strip()
    response = supabase.table("users") \
        .select("id, mac_address, device_name, created_at") \
        .eq("mac_address", mac_normalized) \
        .execute()
    if response.data:
        return response.data[0]
    return None


def get_user_id_by_mac(mac_address: str) -> str | None:
    mac_normalized = mac_address.upper().strip()

    response = supabase.table("users") \
        .select("id") \
        .eq("mac_address", mac_normalized) \
        .execute()

    if response.data:
        return response.data[0]["id"]

    return None
