"""Provider registry: ``config["provider"]`` -> ``LLMClient`` factory.

The defect this fixes: the origin project read ``provider`` into an attribute and then
``_build_provider_client`` imported the Gemini adapter unconditionally, so "swap providers by
editing JSON" was never actually true. Here every provider name resolves through this
registry, so adding or swapping a provider is a one-line addition here and never touches
``Gatekeeper`` or any caller.
"""

from __future__ import annotations

from collections.abc import Callable

from .offline import OfflineClient
from .provider import GeminiClient
from .types import LLMClient

ProviderFactory = Callable[[str, str], LLMClient]


def default_registry() -> dict[str, ProviderFactory]:
    """A fresh, independently-mutable registry mapping provider name to client factory.

    Fresh on every call so a caller (or a test) mutating the returned dict never leaks into
    another caller's registry; ``Gatekeeper`` accepts its own ``registry`` override for tests
    that need a provider with no real SDK behind it.
    """
    return {
        "offline": lambda api_key, model: OfflineClient(),
        "gemini": GeminiClient,
    }
