from __future__ import annotations

from typing import Callable, Dict

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured

from .base import SongGenerationStrategy
from .strategies import MockSongGeneratorStrategy, SunoSongGeneratorStrategy

_CACHE_KEY = "ai_song_domain:generator_strategy_runtime"

VALID_STRATEGY_NAMES = frozenset({"mock", "suno"})


def get_effective_generator_name() -> str:
    cached = cache.get(_CACHE_KEY)
    if cached in VALID_STRATEGY_NAMES:
        return cached
    return (getattr(settings, "GENERATOR_STRATEGY", "mock") or "mock").lower()


def strategy_source() -> str:
    cached = cache.get(_CACHE_KEY)
    return "runtime" if cached in VALID_STRATEGY_NAMES else "environment"


def set_runtime_generator_name(name: str) -> None:
    cache.set(_CACHE_KEY, name.lower(), timeout=60 * 60 * 24 * 365)


def clear_runtime_generator_name() -> None:
    cache.delete(_CACHE_KEY)


def _build_mock() -> SongGenerationStrategy:
    return MockSongGeneratorStrategy()


def _build_suno() -> SongGenerationStrategy:
    api_key = getattr(settings, "SUNO_API_KEY", "") or ""
    if not api_key:
        raise ImproperlyConfigured(
            "Suno mode needs an API key configured for this server."
        )
    return SunoSongGeneratorStrategy(api_key=api_key)


_STRATEGY_FACTORIES: Dict[str, Callable[[], SongGenerationStrategy]] = {
    "mock": _build_mock,
    "suno": _build_suno,
}


def create_song_generator_strategy(name: str) -> SongGenerationStrategy:
    """Factory: instantiate a registered SongGenerationStrategy by name."""
    key = (name or "").lower()
    builder = _STRATEGY_FACTORIES.get(key)
    if builder is None:
        raise ImproperlyConfigured(
            f"Invalid GENERATOR_STRATEGY={name!r}; "
            f"expected one of: {', '.join(sorted(_STRATEGY_FACTORIES))}"
        )
    return builder()


def get_song_generator_strategy() -> SongGenerationStrategy:
    """Effective name (cache override or settings), then factory."""
    return create_song_generator_strategy(get_effective_generator_name())
