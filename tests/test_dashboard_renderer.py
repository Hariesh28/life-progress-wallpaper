import os
from unittest.mock import MagicMock
from life_wallpaper.themes.dashboard import DashboardRenderer
from life_wallpaper.config import AppConfig


def test_dashboard_initialization():
    """Test dashboard initialization."""
    config = AppConfig(
        profile={"name": "Test", "dob": "2000-01-01", "life_expectancy": 80},
        collections={"mantras": [], "footer_quotes": []},
    )
    renderer = DashboardRenderer(config)
    assert renderer.colors["accent"] == (46, 213, 115)  # Verify accent color


def test_dashboard_render_smoke(tmp_path):
    """Smoke test for dashboard generation."""
    original_getcwd = os.getcwd
    try:
        os.getcwd = MagicMock(return_value=str(tmp_path))

        config = AppConfig(
            profile={"name": "Test", "dob": "2000-01-01", "life_expectancy": 80},
            collections={"mantras": [], "footer_quotes": []},
        )
        renderer = DashboardRenderer(config)
        output = renderer.render()
        assert os.path.exists(output)
    finally:
        os.getcwd = original_getcwd
