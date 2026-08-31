import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
SERVICE_DIR = ROOT_DIR / "Service"
CSV_DIR = SERVICE_DIR / "CSV"
DATA_DIR = SERVICE_DIR / "data"
INDEX_PATH = DATA_DIR / "search_index.json"

load_dotenv(ROOT_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
