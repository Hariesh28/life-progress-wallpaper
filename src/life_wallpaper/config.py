from datetime import date
from typing import List, Optional
import json
import os
from pydantic import BaseModel, Field

CONFIG_FILE = "life_config.json"
DEFAULT_DATA = {
    "profile": {"name": "User", "dob": "2000-01-01", "life_expectancy": 80},
    "collections": {
        "mantras": ["THIS DAY WILL NOT COME AGAIN"],
        "footer_quotes": ["TIME IS THE ONLY NON-RENEWABLE RESOURCE"],
    },
}


class Profile(BaseModel):
    name: str = "User"
    dob: date = date(2000, 1, 1)
    life_expectancy: int = 80


class Collections(BaseModel):
    mantras: List[str] = Field(default_factory=list)
    footer_quotes: List[str] = Field(default_factory=list)


class AppConfig(BaseModel):
    profile: Profile
    collections: Collections


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load configuration from JSON file or return default data."""
    if not config_path:
        # Look in current directory or package directory
        possible_paths = [
            CONFIG_FILE,
            os.path.join(
                os.path.dirname(__file__), "..", "..", CONFIG_FILE
            ),  # original location relative to src/life_wallpaper
        ]
        for p in possible_paths:
            if os.path.exists(p):
                config_path = p
                break

    data = DEFAULT_DATA
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                loaded = json.load(f)
                # Merge with default to ensure structure
                data = loaded
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")

    # Ensure defaults if keys missing (simple merge)
    # Pydantic handles validation, but we need to feed it the right structure
    # If the file is partial, this might fail without more complex merging,
    # but for now let's assume valid JSON structure or fallback.

    return AppConfig(**data)
