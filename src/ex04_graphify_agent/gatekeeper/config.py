"""Config-driven loading for the gatekeeper (agent runtime config + paths).

Runtime config (provider, model, rate-limit, retry) comes from ``config/agent.json``; the
runs log dir from ``config/paths.json``. The provider API key is NEVER read here — it is
read from ``os.environ`` (env var named by ``api_key_env``) only, in the client.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any

_AGENT_CONFIG = "config/agent.json"
_PATHS_CONFIG = "config/paths.json"
_RUNS_DIR_KEY = "runs_log_dir"


@functools.cache
def repo_root() -> Path:
    """Walk up from this module to the directory containing ``config/`` (cached)."""
    for parent in Path(__file__).resolve().parents:
        if (parent / _AGENT_CONFIG).is_file():
            return parent
    msg = f"could not locate {_AGENT_CONFIG} above {__file__}"
    raise FileNotFoundError(msg)


def default_agent_config_path() -> Path:
    """The config-driven default agent.json path."""
    return repo_root() / _AGENT_CONFIG


def load_agent_config(path: str | Path | None = None) -> dict[str, Any]:
    """Read the agent runtime config; fail loud if absent."""
    resolved = Path(path) if path is not None else default_agent_config_path()
    if not resolved.is_file():
        msg = f"agent config not found: {resolved}"
        raise FileNotFoundError(msg)
    data: dict[str, Any] = json.loads(resolved.read_text(encoding="utf-8"))
    return data


def default_runs_dir() -> Path:
    """Resolve ``artifacts/runs/`` from ``config/paths.json`` (config-driven)."""
    root = repo_root()
    paths = json.loads((root / _PATHS_CONFIG).read_text(encoding="utf-8"))
    return root / str(paths[_RUNS_DIR_KEY])
