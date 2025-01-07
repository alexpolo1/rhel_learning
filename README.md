# RHEL Learning Script

This project provides a script to manage RHEL learning sessions, including a timer, random questions, and XP tracking.

## Directory Structure

```filetree
rhel_learning
├── src
│   ├── main.py
│   ├── assets
│   │   ├── xp.txt
│   │   ├── level.txt
│   │   ├── session.log
│   │   ├── questions.txt
│   │   └── total_time.txt
│   ├── utils
│   │   ├── __init__.py
│   │   ├── assets.py
│   │   ├── session.py
│   │   ├── steam.py
│   │   ├── timer.py
│   │   └── xp.py
├── requirements.txt
└── README.md
```

## Features

- **Time Tracking**: Tracks total time spent learning and logs each session with timestamps.
- **Gamification**: Earn XP and level up as you complete sessions.
- **Distraction Blocking**: Automatically kills any running Steam processes during your session.
- **Question Reinforcement**: Prompts you with a random RHEL-related question after each session.
- **Session Logs**: Maintains detailed logs of your learning sessions and question answers.

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:
- **Bash Shell** (Default on most Linux systems)
- **wmctrl** (for keeping the browser on top)
  ```bash
  sudo apt install wmctrl
```

## Usage

1. Ensure all necessary files are in place.
2. Install the required dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Run the main script:

   ```sh
   python src/main.py
   ```

## Files

- `main.py`: Entry point for the application.
- `assets.py`: Handles asset initialization and display.
- `session.py`: Handles session logging.
- `steam.py`: Handles killing Steam processes.
- `timer.py`: Handles the timer and asking questions.
- `xp.py`: Handles XP and level-up system.
