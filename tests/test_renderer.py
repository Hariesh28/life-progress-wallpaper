import os
from unittest.mock import MagicMock
from life_wallpaper.renderer import WallpaperRenderer
from life_wallpaper.config import AppConfig


def test_renderer_initialization():
    """Test that renderer initializes without errors using default config."""
    config = AppConfig(
        profile={"name": "Test", "dob": "2000-01-01", "life_expectancy": 80},
        collections={"mantras": ["Mantra"], "footer_quotes": ["Quote"]},
    )
    renderer = WallpaperRenderer(config)
    assert renderer.W == 3840
    assert renderer.H == 2160
    assert renderer.mantra == "Mantra"


def test_render_smoke_test(tmp_path):
    """Smoke test to ensure render runs and produces a file."""
    # We mock os.getcwd to point to tmp_path so the image is saved there
    original_getcwd = os.getcwd
    try:
        os.getcwd = MagicMock(return_value=str(tmp_path))

        config = AppConfig(
            profile={"name": "Test", "dob": "2000-01-01", "life_expectancy": 80},
            collections={"mantras": ["Mantra"], "footer_quotes": ["Quote"]},
        )
        renderer = WallpaperRenderer(config)
        # Mock load_font_family in renderer.utils (or via patch) to avoid system font dependency issues in tests?
        # For now, let's assume it falls back to default safely as written in utils.py.

        output = renderer.render()
        assert os.path.exists(output)

    finally:
        os.getcwd = original_getcwd
