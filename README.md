# ⏳ Life Progress Wallpaper

**Turn your boring desktop into a daily automated reality check.** ⚡

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-GPLv3-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Vibe%20Checked-FF69B4?style=for-the-badge)

---

## 🧐 What is this?

**Life Progress Wallpaper** is a set-and-forget automation tool that keeps you honest. It dynamically generates a clean, aesthetic desktop wallpaper that visualizes your life's progress in years, months, and weeks.

> _"We have two lives, and the second begins when we realize we only have one."_ — Confucius

Every day at midnight, this little bot wakes up, does the math (so you don't have to), updates your wallpaper, and goes back to sleep. It's **unobtrusive**, **battery-friendly**, and honestly, **kind of a vibe**.

### ✨ Why you need this

- **🗓️ It's Consistent**: Updates once a day. No more, no less.
- **🛡️ It's Smart**: Computer triggered a nap? No worries, the Guard Script catches up when you wake it up.
- **🔋 It's Chill**: Runs in seconds and won't drain your battery.
- **🎨 It's Yours**: Customize mantras, quotes, and themes. Use it to manifest greatness or just remind yourself to drink water.
- **🔒 It's Private**: No cloud, no tracking. Just you and your existential dread (optional).

---

## 🚀 Quick Start Guide

### Prerequisites

- **Windows 10 or 11** (The fancy ones)
- **Python 3.8+** (The snake ones)

### Installation

1.  **Clone the Repo**
    Grab the code and get comfy.

    ```bash
    git clone https://github.com/yourusername/life-wallpaper.git
    cd life-wallpaper
    ```

2.  **Setup Environment**
    Let's keep things tidy with a virtual environment.

    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Config Your Life**
    Copy the template so you don't leak your data (we got you).

    ```bash
    cp life_config.example.json life_config.json
    ```

    _(Edit `life_config.json` with your real name and birthday. Don't lie, the math knows.)_

4.  **Activate Automation**
    Right-click `scripts\install_task.ps1` and select **"Run with PowerShell"**.

    > **Boom! 💥** You're done. Your wallpaper will now refresh daily like magic.

---

### 📝 Customizing Your Experience

All settings are stored in `life_config.json`. Think of this as the control center for your daily motivation.

#### Example Configuration

```json
{
  "profile": {
    "name": "Alex",
    "dob": "2000-01-01",
    "life_expectancy": 80
  },
  "collections": {
    "mantras": ["MEMENTO MORI", "STAY HARD", "HYDRATE OR DIEDRATE"],
    "footer_quotes": [
      "The obstacle is the way.",
      "Yesterday you said tomorrow."
    ]
  }
}
```

#### Settings Reference

| Setting           | Type    | Description                                                                |
| :---------------- | :------ | :------------------------------------------------------------------------- |
| `name`            | String  | Your name. Make it epic.                                                   |
| `dob`             | String  | Your birthday (`YYYY-MM-DD`). The engine of the whole operation.           |
| `life_expectancy` | Integer | Total years you're planning on sticking around (default: 80). Aim high! 🚀 |
| `mantras`         | List    | Short vibes for the top of the screen. Randomly picked daily.              |
| `footer_quotes`   | List    | Deep thoughts for the bottom. Also random.                                 |

---

## 🏗️ Under the Hood

For the nerds (we see you), here's how the magic happens:

1.  **The Scheduler**: Windows Task Scheduler is the alarm clock. It rings at **12:00 AM**.
2.  **The Bouncer (`scripts\guard_runner.ps1`)**:
    - This script checks the guest list (`wallpaper_state.json`) to see if we already partied (updated) today.
    - **Already updated?** It goes back to bed.
    - **New day?** It wakes up the Python script.
3.  **The Artist (`src\life_wallpaper`)**:
    - Calculates your life stats.
    - Paints a fresh 4K image using Pillow.
    - Slaps it onto your desktop using Windows APIs.

---

## 🛠️ Troubleshooting

**"Did it run?"**
Check the diary: `wallpaper_activity.log`

**"I want it NOW!"**
Impatient? Force an update:
`.\scripts\run_wallpaper.bat`

**"I'm done with this."**
No hard feelings. Run the uninstaller (as Admin) and we'll clean up our mess:
`.\scripts\uninstall_task.ps1`

---

## 📄 License

This project is free and open-source software licensed under the **GPLv3 License**.

---

_Stay productive. Stay chill._ ✌️
