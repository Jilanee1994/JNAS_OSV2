from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROJECT_NAME = "JNAS AI CORE"
VERSION = "0.1.0"

LLM_PROVIDER = "ollama"

OLLAMA_HOST = "http://127.0.0.1:11434"

DEFAULT_MODEL = "qwen2.5:7b"

WORKSPACE = ROOT / "workspace"
LOG_DIR = ROOT / "logs"
MEMORY_DIR = ROOT / "memory"
PROMPT_DIR = ROOT / "prompts"

WORKSPACE.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)
PROMPT_DIR.mkdir(exist_ok=True)
