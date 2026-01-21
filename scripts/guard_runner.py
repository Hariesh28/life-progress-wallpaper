import json
import os
import subprocess
import sys
import argparse
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import tempfile
import shutil

# --- Configuration ---
# Calculate paths relative to this script (scripts/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
STATE_FILE = os.path.join(PROJECT_ROOT, "wallpaper_state.json")
LOG_FILE = os.path.join(PROJECT_ROOT, "wallpaper_activity.log")
WALLPAPER_MODULE = "life_wallpaper.main"


def setup_logging():
    """Configures logging to both file (rotating) and stdout."""
    logger = logging.getLogger("GuardRunner")
    logger.setLevel(logging.INFO)
    logger.handlers = []  # Clear existing handlers

    # Formatter
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. File Handler (Rotating: 1MB max, keep 3 backups)
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"CRITICAL WARNING: Could not set up file logging: {e}")

    # 2. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def parse_arguments():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(description="Guard Runner for Wallpaper Update")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force execution even if already run today",
    )
    return parser.parse_args()


def load_state(logger):
    """Loads the state file safely."""
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logger.warning(
            f"State file corrupted at {STATE_FILE}. Starting with empty state."
        )
        return {}
    except Exception as e:
        logger.warning(f"Could not read state file: {e}")
        return {}


def save_state(logger, new_state):
    """Saves the state file atomically."""
    try:
        # Write to a temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, dir=PROJECT_ROOT, encoding="utf-8"
        ) as tmp:
            json.dump(new_state, tmp, indent=4)
            tmp_path = tmp.name

        # Atomic move (rename)
        shutil.move(tmp_path, STATE_FILE)
    except Exception as e:
        logger.error(f"Failed to save state file: {e}")
        # Try to clean up temp file if it exists and path is known
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def main():
    logger = setup_logging()
    args = parse_arguments()

    try:
        # 1. Check Previous Execution
        today = datetime.now().strftime("%Y-%m-%d")
        state = load_state(logger)
        last_run_date = state.get("LastRunDate")

        if last_run_date == today and not args.force:
            logger.info(f"Skipping update: Already executed for today ({today}).")
            return 0

        if args.force:
            logger.info("Force flag detected. Bypassing date check.")

        # 2. Execution
        logger.info("Starting wallpaper update...")
        logger.info(f"Module: {WALLPAPER_MODULE}")

        # Use the same python interpreter
        python_exe = sys.executable

        # Run the module
        result = subprocess.run(
            [python_exe, "-m", WALLPAPER_MODULE],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # 3. Log Output
        if result.stdout:
            logger.info(f"OUTPUT:\n{result.stdout.strip()}")
        if result.stderr:
            logger.error(f"ERROR:\n{result.stderr.strip()}")

        if result.returncode == 0:
            logger.info("SUCCESS: Wallpaper updated.")

            # 4. Update State
            new_state = {
                "LastRunDate": today,
                "LastRunTime": datetime.now().strftime("%H:%M:%S"),
            }
            save_state(logger, new_state)
            return 0
        else:
            logger.error(f"FAILURE: Script exited with code {result.returncode}")
            return result.returncode

    except Exception as e:
        logger.exception(f"CRITICAL UNHANDLED ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
