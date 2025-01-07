import time
import random

def show_timer(timer_minutes, questions_file, session_log):
    seconds = timer_minutes * 60
    for i in range(1, seconds + 1):
        print(f"Time remaining: {seconds - i} seconds", end='\r')
        time.sleep(1)
    print("\nSession complete!")
    ask_random_question(questions_file, session_log)

def ask_random_question(questions_file, session_log):
    with open(questions_file, 'r') as f:
        questions = f.readlines()
    random_question = random.choice(questions).strip().split('|')
    question, opt1, opt2, opt3, correct = random_question
    print(question)
    print(f"1. {opt1}")
    print(f"2. {opt2}")
    print(f"3. {opt3}")
    answer = input("Choose an answer (1-3): ")
    with open(session_log, 'a') as f:
        if answer == correct:
            print("Correct answer!")
            f.write(f"{question}|Correct\n")
        else:
            print(f"Wrong answer. The correct option was: {correct}")
            f.write(f"{question}|Wrong\n")
