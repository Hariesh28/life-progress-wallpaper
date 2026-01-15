# Life Progress Wallpaper

An automated desktop wallpaper generator that visualizes your life's progress.
_Turn your desktop into a daily reminder to make every day count._

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/Status-Production--Ready-green)

---

## 📖 Overview

**Life Progress Wallpaper** is a lightweight Python application that dynamically generates a minimalist wallpaper displaying your life progress in years, months, and weeks. It is designed to run silently in the background, updating your desktop wallpaper exactly once per day to keep you mindful of time.

### Key Features

- **Daily Updates**: Automatically updates your wallpaper at midnight (or next wake).
- **Smart Scheduling**: Uses a "Guard Script" to ensure it runs exactly once per calendar day, even across restarts or sleep cycles.
- **Battery Friendly**: Optimized to run quickly and execute even when on battery power.
- **Resilient**: Validates execution and logs activity to prevent errors or duplicate runs.
- **Customizable**: Configurable through `life_config.json`.

---

## 🛠️ Installation & Setup

### Prerequisites

- **Windows 10/11**
- **Python 3.8+** installed and added to PATH.

### Quick Start

1.  **Clone or Download** this repository.
2.  **Initialize Environment**:
    run the setup script (if available) or install dependencies manually:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Configure**:
    Copy `life_config.example.json` to `life_config.json` and edit your details:

    ```bash
    cp life_config.example.json life_config.json
    ```

    _(Edit `life_config.json` with your Name and DOB)_

4.  **Install Automation**:
    Right-click `scripts\install_task.ps1` and select **"Run with PowerShell"**.

    > **What this does:**
    >
    > - Checks for necessary files.
    > - Registers a Windows Scheduled Task named `DailyWallpaperUpdate`.
    > - Sets the task to run daily at **12:00 AM**.
    > - Configures the task to start immediately if the computer was off/sleeping at 12:00 AM.

---

## 🏗️ Architecture

The system consists of three main components:

1.  **Scheduled Task (`DailyWallpaperUpdate`)**:

    - Triggers daily at midnight.
    - Launches the Guard Script hidden in the background.

2.  **Guard Script (`scripts\guard_runner.ps1`)**:

    - **Check**: Reads `wallpaper_state.json` to see if the update ran today.
    - **Decide**:
      - If _Yes_: Exits silently.
      - If _No_: Launches the Python script.
    - **Log**: Records success or failure in `wallpaper_activity.log`.
    - **Update State**: Saves the current date to `wallpaper_state.json`.

3.  **Core Logic (`life_wallpaper.main`)**:
    - Generates the image using Pillow.
    - Sets the Windows Desktop Wallpaper.

---

## 🔍 Troubleshooting

**View Logs:**
Check `wallpaper_activity.log` in the project folder for run history and error messages.

**Manual Run:**
To force an update immediately, you can run the batch file:
`.\scripts\run_wallpaper.bat`

**Reset Schedule:**
If you need to re-register the task, simply run `scripts\install_task.ps1` again. It will overwrite the existing task with the correct settings.

---

## 🗑️ Uninstallation

To remove the scheduled automation and cleanup logs:

1.  Right-click `scripts\uninstall_task.ps1` and select **"Run with PowerShell"**.
    _(Run as Administrator if prompted)_

This will:

- Remove the `DailyWallpaperUpdate` task from Windows Scheduler.
- Delete the `wallpaper_activity.log` and `wallpaper_state.json` files.
- You can then safely delete the project folder if desired.

---

## 📄 License

This project is licensed under the **GPLv3 License**. See the [LICENSE](LICENSE) file for details.
