"""Shared pytest fixtures for the picturesque test suite."""
import glob
import os

import pytest


# ---------------------------------------------------------------------------
# Font fixture
# ---------------------------------------------------------------------------

def _find_system_ttf():
    """Return the path of a regular (non-color) TTF font on this system, or None."""
    search_dirs = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.fonts"),
        os.path.expanduser("~/Library/Fonts"),
        "/Library/Fonts",
        "C:/Windows/Fonts",
    ]
    for d in search_dirs:
        matches = glob.glob(os.path.join(d, "**", "*.ttf"), recursive=True)
        for path in matches:
            # Skip known color/emoji fonts that don't support pixel sizes
            basename = os.path.basename(path).lower()
            if "emoji" in basename or "color" in basename:
                continue
            return path
    return None


@pytest.fixture(scope="session")
def font_path():
    """Path to a real TTF font file.

    Searches common system locations for any .ttf file.  Skips the
    entire test if no font can be found.
    """
    path = _find_system_ttf()
    if path is None:
        pytest.skip("No TTF font found on this system -- skipping font-dependent tests")
    return path
