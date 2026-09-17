"""Compatibility adapters for external career-domain state."""

from .projection import TARGET_REVISION, compile_projection
from .tracker import parse_tracker

__all__ = ["TARGET_REVISION", "compile_projection", "parse_tracker"]
