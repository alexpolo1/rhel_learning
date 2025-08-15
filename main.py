# Migrate questions from file to SQLite if not already present
def migrate_questions_to_sqlite():
    import sqlite3
    if not os.path.exists(QUESTIONS_FILE):
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY,
        category TEXT,
        question TEXT,
        answer1 TEXT,
        answer2 TEXT,
        answer3 TEXT,
        correct_index INTEGER
    )''')
    # Only import if table is empty
    c.execute('SELECT COUNT(*) FROM questions')
    if c.fetchone()[0] == 0:
        with open(QUESTIONS_FILE) as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split('|')]
                if len(parts) == 7:
                    # category|question|a1|a2|a3|correct|explanation
                    category, question = parts[0], parts[1]
                    answers = parts[2:5]
                    correct_index = int(parts[5])
                    explanation = parts[6]
                elif len(parts) == 6:
                    # question|a1|a2|a3|correct|explanation (no category)
                    category = "General"
                    question = parts[0]
                    answers = parts[1:4]
                    correct_index = int(parts[4])
                    explanation = parts[5]
                else:
                    continue
                while len(answers) < 3:
                    answers.append("")
                # Add explanation as a new column if not exists
                try:
                    c.execute('ALTER TABLE questions ADD COLUMN explanation TEXT')
                except Exception:
                    pass
                c.execute('INSERT INTO questions (category, question, answer1, answer2, answer3, correct_index, explanation) VALUES (?, ?, ?, ?, ?, ?, ?)',
                          (category, question, answers[0], answers[1], answers[2], correct_index, explanation))
        conn.commit()
    conn.close()
# Data migration from text files to SQLite
def migrate_txt_to_sqlite():
    migrated = False
    # Migrate XP, level, total_time
    xp = 0
    level = 1
    total_time = 0
    if os.path.exists(XP_FILE):
        try:
            with open(XP_FILE) as f:
                xp = int(f.read().strip() or 0)
        except Exception:
            pass
        migrated = True
    if os.path.exists(LEVEL_FILE):
        try:
            with open(LEVEL_FILE) as f:
                level = int(f.read().strip() or 1)
        except Exception:
            pass
        migrated = True
    if os.path.exists(TOTAL_TIME_FILE):
        try:
            with open(TOTAL_TIME_FILE) as f:
                total_time = int(f.read().strip() or 0)
        except Exception:
            pass
        migrated = True
    # Save to SQLite if any file existed
    if migrated:
        stats = UserStatsSqlite(DB_PATH, SUBSCRIPTION_END_DATE)
        stats.save_stats(xp, level, total_time)
    # Migrate session log
    if os.path.exists(SESSION_LOG):
        stats = UserStatsSqlite(DB_PATH, SUBSCRIPTION_END_DATE)
        try:
            with open(SESSION_LOG) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Try to parse: Session start/end: YYYY-MM-DD HH:MM:SS
                        import re
                        m = re.match(r'Session (\w+): (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                        if m:
                            status, timestamp = m.groups()
                            stats.log_session(status, duration=None)
        except Exception:
            pass
        migrated = True
    # Remove text files
    if migrated:
        for f in [XP_FILE, LEVEL_FILE, TOTAL_TIME_FILE, SESSION_LOG]:
            try:
                os.remove(f)
            except Exception:
                pass


import os
import time
import psutil
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import webbrowser
import random
import sqlite3


TIMER_MINUTES = 30  # Default quiz timer in minutes
# Constants
def show_score_page(score_by_category, total_score):
    # Minimal implementation: show a message box with the score summary
    import tkinter as tk
    from tkinter import messagebox
    summary = f"Total Score: {total_score}\n"
    for cat, (correct, total) in score_by_category.items():
        percent = (correct / total * 100) if total else 0
        summary += f"{cat}: {correct}/{total} ({percent:.0f}%)\n"
    messagebox.showinfo("Quiz Complete", summary)
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, 'assets')
XP_FILE = os.path.join(ASSETS_DIR, 'xp.txt')
LEVEL_FILE = os.path.join(ASSETS_DIR, 'level.txt')
SESSION_LOG = os.path.join(ASSETS_DIR, 'session.log')
TOTAL_TIME_FILE = os.path.join(ASSETS_DIR, 'total_time.txt')
QUESTIONS_FILE = os.path.join(ASSETS_DIR, 'questions.txt')
QUESTIONS_SHUFFLED_FILE = os.path.join(ASSETS_DIR, 'questions_shuffled.txt')
DB_PATH = os.path.join(SCRIPT_DIR, 'rhel_learning.db')
import subprocess
DAYS_LEFT_FROM_FIXED_DATE = 284
FIXED_START_DATE_STR = '2025-08-15'
FIXED_START_DATE = datetime.strptime(FIXED_START_DATE_STR, '%Y-%m-%d')
# Get current system date using 'date' command for reliability
try:
    current_date_str = subprocess.check_output(['date', '+%Y-%m-%d']).decode().strip()
    CURRENT_DATE = datetime.strptime(current_date_str, '%Y-%m-%d')
except Exception:
    CURRENT_DATE = datetime.now()
SUBSCRIPTION_END_DATE = FIXED_START_DATE + timedelta(days=DAYS_LEFT_FROM_FIXED_DATE)

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

# SQLite-based stats and session tracking
class UserStatsSqlite:
    def __init__(self, db_path, subscription_end_date):
        self.db_path = db_path
        self.subscription_end_date = subscription_end_date
        self._ensure_tables()
        self._ensure_user()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_tables(self):
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY,
                xp INTEGER NOT NULL,
                level INTEGER NOT NULL,
                total_time INTEGER NOT NULL
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS session_log (
                id INTEGER PRIMARY KEY,
                status TEXT,
                timestamp TEXT,
                duration INTEGER
            )''')
            conn.commit()

    def _ensure_user(self):
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM user_stats')
            if c.fetchone()[0] == 0:
                c.execute('INSERT INTO user_stats (xp, level, total_time) VALUES (?, ?, ?)', (0, 1, 0))
                conn.commit()

    def get_stats(self):
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('SELECT xp, level, total_time FROM user_stats LIMIT 1')
            return c.fetchone()

    def save_stats(self, xp, level, total_time):
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('UPDATE user_stats SET xp=?, level=?, total_time=? WHERE id=1', (xp, level, total_time))
            conn.commit()

    def add_xp(self, amount):
        xp, level, total_time = self.get_stats()
        xp += amount
        leveled_up = False
        if xp >= level * 100:
            xp -= level * 100
            level += 1
            leveled_up = True
        self.save_stats(xp, level, total_time)
        return xp, level, leveled_up

    def add_time(self, seconds):
        xp, level, total_time = self.get_stats()
        total_time += seconds
        self.save_stats(xp, level, total_time)

    def days_left(self):
        from datetime import datetime
        today = datetime.now()
        return (self.subscription_end_date - today).days

    def log_session(self, status, duration=None):
        import time
        with self._connect() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO session_log (status, timestamp, duration) VALUES (?, ?, ?)',
                      (status, time.strftime('%Y-%m-%d %H:%M:%S'), duration))
            conn.commit()

    def get_total_time(self):
        _, _, total_time = self.get_stats()
        return total_time

    def get_xp_level(self):
        xp, level, _ = self.get_stats()
        return xp, level
import os
import time
import psutil
import tkinter as tk
from tkinter import messagebox

# Utility Functions
def initialize_assets():
    """Ensure all necessary files and directories exist."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    for file_path, default_content in [
        (XP_FILE, '0'),
        (LEVEL_FILE, '1'),
        (SESSION_LOG, ''),
        (TOTAL_TIME_FILE, '0'),
    ]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write(default_content)
    if not os.path.exists(QUESTIONS_FILE):
        raise FileNotFoundError(f"Questions file not found: {QUESTIONS_FILE}")

def log_session(status):
    """Log session start or end with a timestamp."""
    with open(SESSION_LOG, 'a') as f:
        f.write(f"Session {status}: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def display_summary():
    """Display a summary of total time, XP, and level."""
    stats = UserStatsSqlite(DB_PATH, SUBSCRIPTION_END_DATE)
    print(f"Welcome to the RHEL Learning Script!")
    total_time = stats.get_total_time()
    xp, level = stats.get_xp_level()
    print(f"Total session time: {format_time(total_time)}")
    print(f"Current Level: {level}")
    print(f"Current XP: {xp}")
    print(f"Days left: {stats.days_left()}")
    print()
    return total_time, xp, level

def kill_steam():
    """Kill Steam only before the session starts."""
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and "steam" in proc.info['name'].lower():
            print("Stopping Steam...")
            proc.kill()

def update_xp(correct):
    """Update XP and level based on whether the question was answered correctly."""
    stats = UserStatsSqlite(DB_PATH, SUBSCRIPTION_END_DATE)
    if correct:
        xp, level, leveled_up = stats.add_xp(10)
    else:
        xp, level = stats.get_xp_level()
        xp = max(0, xp - 5)
        stats.save_stats(xp, level, stats.get_total_time())
        leveled_up = False
    if correct and leveled_up:
        messagebox.showinfo("LEVEL UP!", f"LEVEL UP! You are now Level {level}!")
    with open(SESSION_LOG, 'a') as f:
        f.write(f"XP and level updated: {xp} XP, Level {level}\n")
    return xp, level

def show_timer(minutes, questions_file, session_log, total_time, xp, level, root):
    # Initialize timer variables BEFORE any inner function definitions
    seconds_left = minutes * 60
    elapsed_time = 0

    def update_timer():
        nonlocal seconds_left, elapsed_time
        if seconds_left > 0:
            seconds_left -= 1
            elapsed_time += 1
            hours, remainder = divmod(seconds_left, 3600)
            minutes_left, seconds = divmod(remainder, 60)
            # Only update timer_label if it still exists
            if timer_label.winfo_exists():
                timer_label.config(text=f"Time left: {hours:02}:{minutes_left:02}:{seconds:02}")
                root.after(1000, update_timer)
        else:
            end_session()

    def update_rol_timer():
        today = datetime.now()
        days_left = (SUBSCRIPTION_END_DATE - today).days
        if rol_label.winfo_exists():
            if days_left > 0:
                rol_label.config(text=f"ROL Subscription: {days_left} days left")
                root.after(60000, update_rol_timer)  # Update every minute
            else:
                rol_label.config(text="ROL Subscription expired!")
                messagebox.showwarning("Subscription Alert", "Your ROL Subscription has expired!")

    def end_session():
        with open(session_log, 'a') as f:
            f.write(f"Session duration: {elapsed_time // 60} minutes and {elapsed_time % 60} seconds\n")
        with open(TOTAL_TIME_FILE, 'w') as f:
            f.write(str(total_time + elapsed_time))
        root.destroy()

    # Function body starts here
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Try to fetch explanation if present
    try:
        c.execute('SELECT id, category, question, answer1, answer2, answer3, correct_index, explanation FROM questions')
        rows = c.fetchall()
        has_explanation = True
    except Exception:
        c.execute('SELECT id, category, question, answer1, answer2, answer3, correct_index FROM questions')
        rows = c.fetchall()
        has_explanation = False
    conn.close()
    if not rows:
        messagebox.showerror("Error", "No questions found in database. Please populate your questions file.")
        root.destroy()
        return
    # Convert to lines format for compatibility
    lines = []
    for row in rows:
        # Compose as: Category|Question|A|B|C|CorrectIndex|Explanation (if present)
        if has_explanation:
            lines.append(f"{row[1]}|{row[2]}|{row[3]}|{row[4]}|{row[5]}|{row[6]}|{row[7]}")
        else:
            lines.append(f"{row[1]}|{row[2]}|{row[3]}|{row[4]}|{row[5]}|{row[6]}")

    # Track per-category score
    score_by_category = {}
    total_correct = 0
    total_questions = 0
    max_score = 300


    # Shuffle and use each question only once per session
    random.shuffle(lines)
    questions_to_ask = lines.copy()

    # Create a frame for question/answer widgets ONCE
    question_frame = tk.Frame(root)
    question_frame.pack(pady=10)

    # Add a label to show per-category progress
    progress_label = tk.Label(root, text="", font=("Helvetica", 10), fg="blue")
    progress_label.pack(pady=2)

    def update_progress_label():
        # Always show progress for each category, even if empty
        progress_items = []
        all_cats = set(score_by_category.keys())
        for q in lines:
            cat = q.split('|')[0] if q.split('|')[0] else "General"
            all_cats.add(cat)
        for cat in sorted(all_cats):
            correct, total = score_by_category.get(cat, [0, 0])
            progress_items.append(f"{cat[:3].upper()}:{correct}/{total}")
        # Break into multiple lines if too many categories
        max_per_line = 7
        lines_out = ["  |  ".join(progress_items[i:i+max_per_line]) for i in range(0, len(progress_items), max_per_line)]
        progress_label.config(text="\n".join(lines_out))

    def ask_next_question():
        nonlocal total_questions, total_correct
        if not questions_to_ask:
            # Show score page at end
            total_score = int((total_correct / total_questions) * max_score) if total_questions else 0
            root.destroy()
            show_score_page(score_by_category, total_score)
            return
        qline = questions_to_ask.pop(0)
        parts = qline.split('|')
        if len(parts) < 5:
            ask_next_question()
            return

        # Assume format: Category|Question|A|B|C|CorrectIndex|Explanation (optional)
        category = parts[0] if parts[0] else "General"
        question_text = parts[1]
        answers = parts[2:-1] if len(parts) < 7 else parts[2:-2]
        correct_idx = int(parts[-2]) - 1 if len(parts) >= 7 else int(parts[-1]) - 1
        explanation = parts[-1] if len(parts) >= 7 else None

        # Build a list of (text, is_correct) and shuffle
        opts = []
        for idx, ans in enumerate(answers):
            if ans.strip():
                opts.append({'text': ans, 'correct': (idx == correct_idx)})
        random.shuffle(opts)

        # Clear previous question/answer widgets only
        for widget in question_frame.winfo_children():
            widget.destroy()

        # Show only the question text (not category)
        question_label = tk.Label(question_frame, text=question_text, font=("Helvetica", 14))
        question_label.pack(pady=10)

        answer_var = tk.StringVar(value="")
        radio_buttons = []
        for opt in opts:
            rb = tk.Radiobutton(question_frame, text=opt['text'],
                                variable=answer_var, value=opt['text'],
                                font=("Helvetica", 12))
            rb.pack(anchor='w')
            radio_buttons.append(rb)

        def check_answer():
            nonlocal total_questions, total_correct
            sel = answer_var.get()
            correct = any(o['text'] == sel and o['correct'] for o in opts)
            # Find the correct answer
            correct_answer = None
            for o in opts:
                if o['correct']:
                    correct_answer = o['text']
                    break
            # Use explanation if present, else fallback
            if explanation:
                detail = explanation
            else:
                detail = f"The correct answer is: {correct_answer}"
            if correct:
                messagebox.showinfo("Correct!", f"You chose the right answer.\n{detail}")
                new_xp, new_level = update_xp(True)
                score_by_category.setdefault(category, [0, 0])[0] += 1
                total_correct += 1
                score_by_category.setdefault(category, [0, 0])[1] += 1
                total_questions += 1
                for b in radio_buttons: b.config(state=tk.DISABLED)
                xp_label.config(text=f"XP: {new_xp}")
                level_label.config(text=f"Level: {new_level}")
                update_progress_label()
                root.after(500, ask_next_question)
            else:
                new_xp, new_level = update_xp(False)
                score_by_category.setdefault(category, [0, 0])[1] += 1
                total_questions += 1
                xp_label.config(text=f"XP: {new_xp}")
                level_label.config(text=f"Level: {new_level}")
                update_progress_label()
                # Show explanation, then immediately go to next question after dialog closes
                def after_incorrect():
                    ask_next_question()
                messagebox.showinfo("Incorrect", f"Sorry, that's not correct.\n{detail}")
                root.after(10, after_incorrect)

        submit_btn = tk.Button(question_frame, text="Submit", command=check_answer)
        submit_btn.pack(pady=5)

    stats = UserStatsSqlite(DB_PATH, SUBSCRIPTION_END_DATE)
    timer_label = tk.Label(root, text=f"Time left: {minutes:02}:00:00", font=("Helvetica", 16))
    timer_label.pack(pady=20)

    rol_label = tk.Label(root, text=f"ROL Subscription: {stats.days_left()} days left", font=("Helvetica", 14), fg="red")
    rol_label.pack(pady=5)

    xp_val, level_val = stats.get_xp_level()
    xp_label = tk.Label(root, text=f"XP: {xp_val}", font=("Helvetica", 14))
    xp_label.pack(pady=5)

    level_label = tk.Label(root, text=f"Level: {level_val}", font=("Helvetica", 14))
    level_label.pack(pady=5)

    total_time_label = tk.Label(root, text=f"Total session time: {format_time(stats.get_total_time())}", font=("Helvetica", 14))
    total_time_label.pack(pady=5)

    def update_total_time_label():
        nonlocal elapsed_time
        # Show total time as (previous total + elapsed this session)
        current_total = stats.get_total_time() + elapsed_time
        total_time_label.config(text=f"Total session time: {format_time(current_total)}")
        root.after(1000, update_total_time_label)

    # Start the first question and live-updating total time
    update_progress_label()
    update_total_time_label()
    ask_next_question()

    def periodic_kill_steam():
        kill_steam()
        root.after(10000, periodic_kill_steam)

    root.after(1000, update_timer)
    root.after(1000, update_rol_timer)
    root.after(10000, periodic_kill_steam)

## Removed open_firefox, use open_learning_links instead

def shuffle_questions(input_file, output_file):
    """Shuffle questions and answers, updating the correct answer index."""
    with open(input_file) as f:
        lines = [l.strip() for l in f if l.strip()]

    with open(output_file, 'w') as f:
        for line in lines:
            parts = line.split('|')
            # Handle both with and without category
            if len(parts) == 6:
                # category|question|a1|a2|a3|correct
                category, question = parts[0], parts[1]
                answers = parts[2:5]
                correct = int(parts[5])
            elif len(parts) == 5:
                # question|a1|a2|a3|correct (no category)
                category = "General"
                question = parts[0]
                answers = parts[1:4]
                correct = int(parts[4])
            else:
                continue  # skip malformed
            zipped = list(zip(answers, range(1, len(answers)+1)))
            random.shuffle(zipped)
            new_answers, old_indices = zip(*zipped)
            new_correct = old_indices.index(correct) + 1
            f.write(f"{category}|{question}|{'|'.join(new_answers)}|{new_correct}\n")

def open_learning_links():
    urls = [
        "https://rol.redhat.com",
        "https://docs.google.com/spreadsheets/d/1ZQpE1fQoc-lyElFmvoQLW-2tOclMsMENYKiehu3jrxc/edit?gid=0#gid=0"
    ]
    for url in urls:
        webbrowser.open_new_tab(url)

def main():
    migrate_txt_to_sqlite()
    migrate_questions_to_sqlite()
    initialize_assets()
    log_session("start")
    total_time, xp, level = display_summary()
    kill_steam()
    # open_firefox removed; open_learning_links is used instead
    # Always open learning links on startup
    open_learning_links()
    root = tk.Tk()
    root.title("RHEL Learning Timer")

    def on_closing():
        log_session("end")
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    try:
        show_timer(TIMER_MINUTES, QUESTIONS_SHUFFLED_FILE, SESSION_LOG, total_time, xp, level, root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        log_session("end")

if __name__ == "__main__":
    shuffle_questions(QUESTIONS_FILE, QUESTIONS_SHUFFLED_FILE)
    main()

