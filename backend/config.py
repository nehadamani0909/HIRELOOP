from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent


def load_backend_env() -> None:
    load_dotenv(BACKEND_DIR / ".env")
