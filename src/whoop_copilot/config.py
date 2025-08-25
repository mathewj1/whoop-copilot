import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv


APP_DIR = Path(os.path.expanduser("~/.whoop-copilot"))
TOKENS_PATH = APP_DIR / "tokens.json"


def ensure_app_dirs() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    # Load .env from project root if present
    load_dotenv()


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    return os.getenv(name, default)


def read_tokens() -> Dict[str, Any]:
    ensure_app_dirs()
    if TOKENS_PATH.exists():
        try:
            return json.loads(TOKENS_PATH.read_text())
        except Exception:
            return {}
    return {}


def write_tokens(tokens: Dict[str, Any]) -> None:
    ensure_app_dirs()
    TOKENS_PATH.write_text(json.dumps(tokens, indent=2))


def get_default_redirect_port() -> int:
    port_str = get_env("REDIRECT_PORT", "8080")
    try:
        return int(port_str)
    except Exception:
        return 8080


