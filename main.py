import os
import time
import psutil
import tkinter as tk
from tkinter import messagebox
import random

# Utility functions
def initialize_assets(assets_dir, xp_file, level_file, session_log, total_time_file, questions_file):
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    if not os.path.exists(xp_file):
        with open(xp_file, 'w') as f:
            f.write('0')
    if not os.path.exists(level_file):
        with open(level_file, 'w') as f:
            f.write('1')
    if not os.path.exists(session_log):
        open(session_log, 'w').close()
    if not os.path.exists(total_time_file):
        with open(total_time_file, 'w') as f:
            f.write('0')
    if not os.path.exists(questions_file):
        raise FileNotFoundError(f"Questions file not found: {questions_file}")

def log_session(session_log, status):
    with open(session_log, 'a') as f:
        f.write(f"Session {status}: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def display_summary(total_time_file, xp_file, level_file):
    with open(total_time_file, 'r') as f:
        total_time = int(f.read().strip())
    with open(xp_file, 'r') as f:
        xp = int(f.read().strip())
    with open(level_file, 'r') as f:
        level = int(f.read().strip())
    hours, minutes = divmod(total_time, 60)
    print(f"Welcome to the RHEL Learning Script!")
    print(f"Total session time: {hours} hours and {minutes} minutes.")
    print(f"Current Level: {level}")
    print(f"Current XP: {xp}")
    print()

def kill_steam():
    for proc in psutil.process_iter():
        if proc.name() == "steam.exe":
            proc.kill()

def update_xp(xp_file, level_file, session_log, correct):
    with open(xp_file, 'r') as f:
        xp = int(f.read().strip())
    with open(level_file, 'r') as f:
        level = int(f.read().strip())
    if correct:
        new_xp = xp + 10
    else:
        new_xp = max(0, xp - 5)  # Ensure XP doesn't go below 0
    if new_xp >= level * 100:
        level += 1
        new_xp -= (level - 1) * 100
        print(f"LEVEL UP! You are now Level {level}!")
    with open(xp_file, 'w') as f:
        f.write(str(new_xp))
    with open(level_file, 'w') as f:
        f.write(str(level))
    with open(session_log, 'a') as f:
        f.write(f"XP and level updated: {new_xp} XP, Level {level}\n")

def show_timer(minutes, questions_file, session_log):
    def update_timer():
        nonlocal seconds_left
        if seconds_left > 0:
            seconds_left -= 1
            hours, remainder = divmod(seconds_left, 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_label.config(text=f"Time left: {hours:02}:{minutes:02}:{seconds:02}")
            root.after(1000, update_timer)
        else:
            messagebox.showinfo("Time's up!", "The session has ended.")
            with open(session_log, 'a') as f:
                f.write(f"Session duration: {minutes} minutes\n")
            root.destroy()

    def check_answer():
        selected_answer = answer_var.get()
        if selected_answer == correct_answer:
            messagebox.showinfo("Correct!", "You selected the correct answer.")
            update_xp(XP_FILE, LEVEL_FILE, SESSION_LOG, correct=True)
        else:
            messagebox.showinfo("Incorrect", "You selected the wrong answer.")
            update_xp(XP_FILE, LEVEL_FILE, SESSION_LOG, correct=False)

    root = tk.Tk()
    root.title("RHEL Learning Timer")

    seconds_left = minutes * 60

    timer_label = tk.Label(root, text=f"Time left: {minutes:02}:00:00", font=("Helvetica", 16))
    timer_label.pack(pady=20)

    with open(questions_file, 'r') as f:
        questions = f.readlines()

    question = random.choice(questions).strip()
    question_text, *answers, correct_answer = question.split('|')

    question_label = tk.Label(root, text=f"Question: {question_text}", font=("Helvetica", 14))
    question_label.pack(pady=10)

    answer_var = tk.StringVar(value="")

    for idx, answer in enumerate(answers, start=1):
        radio_button = tk.Radiobutton(root, text=answer, variable=answer_var, value=str(idx), font=("Helvetica", 12))
        radio_button.pack(anchor='w')

    submit_button = tk.Button(root, text="Submit", command=check_answer, font=("Helvetica", 12))
    submit_button.pack(pady=10)

    root.after(1000, update_timer)
    root.mainloop()

# Constants
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, 'assets')
XP_FILE = os.path.join(ASSETS_DIR, 'xp.txt')
LEVEL_FILE = os.path.join(ASSETS_DIR, 'level.txt')
SESSION_LOG = os.path.join(ASSETS_DIR, 'session.log')
QUESTIONS_FILE = os.path.join(ASSETS_DIR, 'questions.txt')
TOTAL_TIME_FILE = os.path.join(ASSETS_DIR, 'total_time.txt')
URL = "https://rol.redhat.com"
TIMER_MINUTES = 20

def main():
    # Initialize assets
    initialize_assets(ASSETS_DIR, XP_FILE, LEVEL_FILE, SESSION_LOG, TOTAL_TIME_FILE, QUESTIONS_FILE)

    # Log session start
    log_session(SESSION_LOG, "start")

    # Display session summary
    display_summary(TOTAL_TIME_FILE, XP_FILE, LEVEL_FILE)

    # Start killing Steam processes in the background
    kill_steam()

    # Start session
    print("Starting RHEL Learning Session...")
    show_timer(TIMER_MINUTES, QUESTIONS_FILE, SESSION_LOG)

    # Log session end
    log_session(SESSION_LOG, "end")

if __name__ == "__main__":
    main()
