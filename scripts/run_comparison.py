"""Manual, key-gated real-numbers run: graph-guided vs naive (PHASE6-060..063, TC-T8).

Produces the real R5.6/R7.8 token-comparison numbers from an actual provider call. The
test suite NEVER invokes this path (ADR-0005): if the provider key env var named by
``config/agent.json`` ``api_key_env`` is unset, this script exits with a clear "key
required" message and does nothing else. Usage: ``uv run python scripts/run_comparison.py``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from ex04_graphify_agent.gatekeeper.config import load_agent_config  # noqa: E402


def _load_local_env() -> None:
    """Load a local ``.env`` (manual real run only) so the provider key reaches os.environ.

    Invoked solely from ``__main__`` below — never from ``main()`` — so the keyless test
    suite (ADR-0005) never auto-loads a developer's local key. ``.env`` is gitignored;
    the key is read from ``os.environ`` by the gatekeeper, never from any config file.
    """
    load_dotenv()


def _missing_key_message(env_var: str) -> str:
    return (
        f"run_comparison: provider API key required - set {env_var} before running this "
        "script (ADR-0005: the keyless test suite never triggers this path)."
    )


def main(argv: list[str] | None = None) -> int:
    """Exit 1 with a clear message if the configured provider key is absent (TC-T8)."""
    config = load_agent_config()
    env_var = str(config.get("api_key_env", ""))
    if not env_var or not os.environ.get(env_var):
        print(_missing_key_message(env_var or "<api_key_env unset in config/agent.json>"))
        return 1
    return _run_real_comparison()


def _run_real_comparison() -> int:  # pragma: no cover - requires a real provider key
    """Run both routes with the real provider, write the report + token logs."""
    from ex04_graphify_agent.sdk import Ex04Sdk

    path = Ex04Sdk().compare_tokens()
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    _load_local_env()
    raise SystemExit(main(sys.argv[1:]))
