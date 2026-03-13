"""Shared fixtures for libgranola tests.

Uses the real Granola cache on the local machine.  Tests are skipped
if the cache file is not present.
"""

from __future__ import annotations

from pathlib import Path

import pytest

CACHE_DIR = Path.home() / "Library" / "Application Support" / "Granola"


@pytest.fixture(scope="session")
def store():
    """Session-scoped GranolaStore loaded from the real cache."""
    if not any(CACHE_DIR.glob("cache-v*.json")):
        pytest.skip("Granola cache not found")

    from libgranola import GranolaStore

    return GranolaStore()
