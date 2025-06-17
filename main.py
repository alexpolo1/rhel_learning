import os
import time
import psutil
import tkinter as tk
from tkinter import messagebox
import random
import subprocess
from datetime import datetime, timedelta
import webbrowser

# Constants
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, 'assets')
XP_FILE = os.path.join(ASSETS_DIR, 'xp.txt')
LEVEL_FILE = os.path.join(ASSETS_DIR, 'level.txt')
SESSION_LOG = os.path.join(ASSETS_DIR, 'session.log')
QUESTIONS_FILE = os.path.join(ASSETS_DIR, 'questions.txt')
QUESTIONS_SHUFFLED_FILE = os.path.join(ASSETS_DIR, 'questions_shuffled.txt')
TOTAL_TIME_FILE = os.path.join(ASSETS_DIR, 'total_time.txt')
URL = "https://rol.redhat.com"
TIMER_MINUTES = 60

# Set the ROL subscription expiration date
SUBSCRIPTION_END_DATE = datetime.now() + timedelta(days=343)

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
    try:
        with open(TOTAL_TIME_FILE, 'r') as f:
            total_time = int(f.read().strip() or 0)
    except FileNotFoundError:
        total_time = 0

    try:
        with open(XP_FILE, 'r') as f:
            xp = int(f.read().strip() or 0)
    except FileNotFoundError:
        xp = 0

    try:
        with open(LEVEL_FILE, 'r') as f:
            level = int(f.read().strip() or 1)
    except FileNotFoundError:
        level = 1

    hours, remainder = divmod(total_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Welcome to the RHEL Learning Script!")
    print(f"Total session time: {hours} hours, {minutes} minutes, and {seconds} seconds.")
    print(f"Current Level: {level}")
    print(f"Current XP: {xp}")
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
    with open(XP_FILE, 'r') as f:
        xp = int(f.read().strip() or 0)
    with open(LEVEL_FILE, 'r') as f:
        level = int(f.read().strip() or 1)

    if correct:
        xp += 10
    else:
        xp = max(0, xp - 5)

    if xp >= level * 100:
        level += 1
        xp -= (level - 1) * 100
        messagebox.showinfo("LEVEL UP!", f"LEVEL UP! You are now Level {level}!")

    with open(XP_FILE, 'w') as f:
        f.write(str(xp))
    with open(LEVEL_FILE, 'w') as f:
        f.write(str(level))

    with open(SESSION_LOG, 'a') as f:
        f.write(f"XP and level updated: {xp} XP, Level {level}\n")

    return xp, level

def show_timer(minutes, questions_file, session_log, total_time, xp, level, root):
    def update_timer():
        nonlocal seconds_left, elapsed_time
        if seconds_left > 0:
            seconds_left -= 1
            elapsed_time += 1
            hours, remainder = divmod(seconds_left, 3600)
            minutes_left, seconds = divmod(remainder, 60)
            timer_label.config(text=f"Time left: {hours:02}:{minutes_left:02}:{seconds:02}")
            root.after(1000, update_timer)
        else:
            end_session()

    def update_rol_timer():
        today = datetime.now()
        days_left = (SUBSCRIPTION_END_DATE - today).days

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

    def on_closing():
        end_session()

    # Load & parse questions
    with open(questions_file, 'r') as f:
        lines = [l.strip() for l in f if l.strip()]
    question_line = random.choice(lines)
    parts = question_line.split('|')
    question_text = parts[0]
    answers = parts[1:-1]
    correct_idx = int(parts[-1]) - 1  # zero-based

    # Build a list of (text, is_correct) and shuffle
    opts = []
    for idx, ans in enumerate(answers):
        opts.append({'text': ans, 'correct': (idx == correct_idx)})
    random.shuffle(opts)

    # Display question
    question_label = tk.Label(root, text=f"Question: {question_text}", font=("Helvetica", 14))
    question_label.pack(pady=10)

    answer_var = tk.StringVar(value="")
    radio_buttons = []
    for opt in opts:
        rb = tk.Radiobutton(root, text=opt['text'],
                            variable=answer_var, value=opt['text'],
                            font=("Helvetica", 12))
        rb.pack(anchor='w')
        radio_buttons.append(rb)

    def check_answer():
        sel = answer_var.get()
        correct = any(o['text'] == sel and o['correct'] for o in opts)
        if correct:
            messagebox.showinfo("Correct!", "You chose the right answer.")
            new_xp, new_level = update_xp(True)
        else:
            messagebox.showinfo("Incorrect", "Sorry, that’s not correct.")
            new_xp, new_level = update_xp(False)
        for b in radio_buttons: b.config(state=tk.DISABLED)
        xp_label.config(text=f"XP: {new_xp}")
        level_label.config(text=f"Level: {new_level}")

    submit_btn = tk.Button(root, text="Submit", command=check_answer)
    submit_btn.pack(pady=5)

    def periodic_kill_steam():
        kill_steam()
        root.after(10000, periodic_kill_steam)

    seconds_left = minutes * 60
    elapsed_time = 0

    # GUI Components
    timer_label = tk.Label(root, text=f"Time left: {minutes:02}:00:00", font=("Helvetica", 16))
    timer_label.pack(pady=20)

    rol_label = tk.Label(root, text="ROL Subscription: Calculating...", font=("Helvetica", 14), fg="red")
    rol_label.pack(pady=5)

    xp_label = tk.Label(root, text=f"XP: {xp}", font=("Helvetica", 14))
    xp_label.pack(pady=5)

    level_label = tk.Label(root, text=f"Level: {level}", font=("Helvetica", 14))
    level_label.pack(pady=5)

    total_time_label = tk.Label(root, text=f"Total session time: {total_time // 3600} hours, {(total_time % 3600) // 60} minutes, and {total_time % 60} seconds", font=("Helvetica", 14))
    total_time_label.pack(pady=5)

    root.after(1000, update_timer)
    root.after(1000, update_rol_timer)
    root.after(10000, periodic_kill_steam)

def open_firefox(url):
    print(f"Attempting to open Firefox with URL: {url}")
    if 'DISPLAY' in os.environ:
        try:
            subprocess.Popen(['firefox', '--new-window', url], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print("Firefox opened successfully.")
        except subprocess.CalledProcessError:
            print("Firefox is already running. Reusing the existing instance.")
            subprocess.Popen(['firefox', '--new-tab', url], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    else:
        print("No graphical environment detected. Skipping browser opening.")

def shuffle_questions(input_file, output_file):
    """Shuffle questions and answers, updating the correct answer index."""
    with open(input_file) as f:
        lines = [l.strip() for l in f if l.strip()]

    with open(output_file, 'w') as f:
        for line in lines:
            parts = line.split('|')
            q, answers, correct = parts[0], parts[1:-1], int(parts[-1])
            zipped = list(zip(answers, range(1, len(answers)+1)))
            random.shuffle(zipped)
            new_answers, old_indices = zip(*zipped)
            new_correct = old_indices.index(correct) + 1
            f.write(f"{q}|{'|'.join(new_answers)}|{new_correct}\n")

def open_learning_links():
    urls = [
        "https://rol.redhat.com",
        "https://docs.google.com/spreadsheets/d/1ZQpE1fQoc-lyElFmvoQLW-2tOclMsMENYKiehu3jrxc/edit?gid=0#gid=0"
    ]
    for url in urls:
        webbrowser.open_new_tab(url)

def main():
    initialize_assets()
    log_session("start")
    total_time, xp, level = display_summary()
    kill_steam()
    open_firefox(URL)
    open_learning_links()
    root = tk.Tk()
    root.title("RHEL Learning Timer")
    root.protocol("WM_DELETE_WINDOW", lambda: log_session(...))
    show_timer(TIMER_MINUTES, QUESTIONS_SHUFFLED_FILE, SESSION_LOG, total_time, xp, level, root)
    log_session("end")
    root.mainloop()

if __name__ == "__main__":
    shuffle_questions(QUESTIONS_FILE, QUESTIONS_SHUFFLED_FILE)
    main()

