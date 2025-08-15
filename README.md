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

# RHEL Learning Quiz App

This is a Python-based quiz application for learning Red Hat Enterprise Linux (RHEL) concepts, including scenario-based RHCSA questions. The app tracks your XP, level, and total study time, and provides explanations for each answer to help you learn more effectively.

## Features

- Scenario-based RHCSA questions (imported from `assets/questions.txt`)
- XP and level tracking (XP: +10 for correct, -5 for incorrect; level up every 100 XP)
- Total study time tracking
- Explanations shown after each answer (7th field in questions)
- SQLite database for persistent stats, session logs, and questions
- GUI built with Tkinter
- Automatic migration from legacy text files to SQLite
- All questions shown in each session, in random order

## Getting Started

1. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Add your questions:**
   - Edit `assets/questions.txt` with your questions in the format:
     ```
     Category|Question|Answer1|Answer2|Answer3|CorrectIndex|Explanation
     ```
     - `CorrectIndex` is 1-based (1, 2, or 3)
     - `Explanation` is a short explanation shown after each answer

3. **Run the app:**
   ```sh
   python main.py
   ```

## How It Works

- On first run, the app migrates your XP, level, and total time from text files to SQLite (if present).
- Questions are imported from `assets/questions.txt` into the SQLite database, including explanations.
- All questions are shuffled and presented in a random order each session.
- After each answer, an explanation is shown to help you learn.
- XP and level are updated based on your answers (correct: +10 XP, incorrect: -5 XP, level up every 100 XP).
- Your total study time and session logs are tracked in the database.
- At the end of the session, a summary of your score by category is shown.

## File Structure

- `main.py` - Main application logic
- `assets/questions.txt` - Source of all questions (with explanations)
- `assets/questions_shuffled.txt` - Shuffled questions for each session
- `rhel_learning.db` - SQLite database for stats, session logs, and questions
- `requirements.txt` - Python dependencies

## Question Format

Each line in `assets/questions.txt` should be:

```
Category|Question|Answer1|Answer2|Answer3|CorrectIndex|Explanation
```

- `Category`: e.g., "User Management", "Networking", etc.
- `Question`: The question text
- `Answer1`, `Answer2`, `Answer3`: Multiple choice answers
- `CorrectIndex`: 1-based index of the correct answer (1, 2, or 3)
- `Explanation`: Shown after each answer for learning

## Troubleshooting

- Make sure your `assets/questions.txt` includes explanations as the 7th field for each question.
- The app requires Python 3 and Tkinter.
- If you encounter errors, check that your questions file is formatted correctly and all dependencies are installed.
- The app will automatically migrate your old XP, level, and time files to SQLite on first run.

## License

MIT License
