import os
from dotenv import load_dotenv
load_dotenv()

APP_NAME = "VIRALMIND AI"
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///viralmind.db")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
