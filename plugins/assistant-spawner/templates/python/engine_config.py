"""Global assistant-engine configuration shared by bots and scripts."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any

log = logging.getLogger(__name__)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_CONFIG_FILE = os.path.join(PROJECT_DIR, "memory", ".assistant-engine.json")

ENGINE_CLAUDE = "claude"
ENGINE_CODEX = "codex"
ALLOWED_ENGINES = {ENGINE_CLAUDE, ENGINE_CODEX}

_UNSET = object()


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _default_state() -> dict[str, Any]:
    return {
        "version": 1,
        "engine": ENGINE_CLAUDE,
        "models": {
            ENGINE_CLAUDE: None,
            ENGINE_CODEX: "gpt-5.4",
        },
        "updated_at": _now_iso(),
        "updated_by": "system:default",
    }


def _atomic_write(path: str, data: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def _normalize_state(data: dict[str, Any]) -> dict[str, Any]:
    state = _default_state()

    engine = str(data.get("engine", state["engine"]).lower())
    if engine in ALLOWED_ENGINES:
        state["engine"] = engine

    models = data.get("models", {})
    if isinstance(models, dict):
        for eng in ALLOWED_ENGINES:
            value = models.get(eng, state["models"][eng])
            state["models"][eng] = value if (value is None or isinstance(value, str)) else state["models"][eng]

    updated_at = data.get("updated_at")
    if isinstance(updated_at, str) and updated_at:
        state["updated_at"] = updated_at

    updated_by = data.get("updated_by")
    if isinstance(updated_by, str) and updated_by:
        state["updated_by"] = updated_by

    return state


def get_engine_state() -> dict[str, Any]:
    """Load and normalize global engine state with safe defaults."""
    if not os.path.exists(ENGINE_CONFIG_FILE):
        state = _default_state()
        _atomic_write(ENGINE_CONFIG_FILE, state)
        return state

    try:
        with open(ENGINE_CONFIG_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            raise ValueError("engine config root must be an object")
    except Exception as e:
        log.warning("Failed to read engine config (%s), using defaults", e)
        state = _default_state()
        _atomic_write(ENGINE_CONFIG_FILE, state)
        return state

    state = _normalize_state(raw)
    if state != raw:
        _atomic_write(ENGINE_CONFIG_FILE, state)
    return state


def set_engine_state(engine: str, *, model: str | None | object = _UNSET,
                     updated_by: str = "system") -> dict[str, Any]:
    """Set global engine and optionally update model for that engine.

    Pass model=None to clear an engine-specific model override.
    """
    engine_norm = (engine or "").strip().lower()
    if engine_norm not in ALLOWED_ENGINES:
        raise ValueError(f"engine must be one of: {', '.join(sorted(ALLOWED_ENGINES))}")

    state = get_engine_state()
    state["engine"] = engine_norm

    if model is not _UNSET:
        if model is None:
            state["models"][engine_norm] = None
        else:
            model_str = str(model).strip()
            state["models"][engine_norm] = model_str or None

    state["updated_at"] = _now_iso()
    state["updated_by"] = updated_by
    _atomic_write(ENGINE_CONFIG_FILE, state)
    return state


def get_effective_engine_and_model(*, model_override: str | None = None) -> tuple[str, str | None]:
    """Return (engine, model) based on global state and optional override."""
    state = get_engine_state()
    engine = state["engine"]
    if model_override is not None:
        return engine, model_override
    return engine, state["models"].get(engine)
