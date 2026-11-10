"""Environment helpers and path defaults for PSB legal assistant."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORGANIZER_KB = ROOT / "data" / "organizer" / "kb"
FIXTURE_KB = ROOT / "data" / "fixtures" / "kb.jsonl"
CHUNK_CHARS = 700
QUOTE_CHARS = 700
MAX_ANSWER_CHARS = 10_000
MAX_QUESTION_CHARS = 4000
LLM_TIMEOUT_SEC = 60
FALLBACK_ANSWER = (
    "Не удалось сформировать ответ по базе знаний. Повторите запрос или уточните формулировку."
)


def load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VALUE from .env into os.environ if not already set. No secret logging."""
    env_path = path or (ROOT / ".env")
    if not env_path.is_file():
        return
    try:
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if not key or key in os.environ:
                continue
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            os.environ[key] = value
    except OSError:
        return


load_dotenv()


def env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value and value != name:
            return value
    return default


def env_int(name: str, default: int, low: int | None = None, high: int | None = None) -> int:
    try:
        value = int(env(name, default=str(default)) or default)
    except ValueError:
        value = default
    if low is not None:
        value = max(low, value)
    if high is not None:
        value = min(high, value)
    return value


def data_dir() -> Path:
    raw = env("DATA_DIR", default="data")
    path = Path(raw)
    return path if path.is_absolute() else (ROOT / path)


def llm_configured() -> bool:
    base = env("LLM_BASE_URL", "BASE_URL", "OPENAI_BASE_URL")
    key = env("LLM_API_KEY", "OPENAI_API_KEY")
    return bool(base and key)


def llm_settings() -> tuple[str, str, str]:
    base = env("LLM_BASE_URL", "BASE_URL", "OPENAI_BASE_URL").rstrip("/")
    key = env("LLM_API_KEY", "OPENAI_API_KEY")
    model = env("LLM_MODEL", "GEN_MODEL", "OPENAI_MODEL", default="deepseek-chat")
    return base, key, model
