"""Provider-agnostic LLM client wrapper (Gemini adapter behind it). Stub — Phase 3.

The concrete provider is named by config/agent.json; the key comes from os.environ only.
Keyless mode injects a deterministic mock (ADR-0005).
"""
