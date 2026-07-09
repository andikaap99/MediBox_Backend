from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_API_URL = os.getenv("QWEN_API_URL")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chromadb")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "medibox_obat")
JWT_SECRET = os.getenv("JWT_SECRET", "medibox-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24