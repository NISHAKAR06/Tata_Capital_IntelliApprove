"""Deprecated configuration shim for legacy LLM imports.

New code should use settings and the Ollama client directly.
"""

from __future__ import annotations


def __getattr__(name):  # pragma: no cover - defensive stub
    raise RuntimeError("Deprecated module; use app.config.settings and app.config.ollama_client instead.")
