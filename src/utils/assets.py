import os

def initialize_assets(assets_dir, xp_file, level_file, session_log, total_time_file, questions_file):
    if not os.path.isdir(assets_dir):
        print(f"Assets directory not found: {assets_dir}")
        print("Please create the 'assets' folder and include the required files:")
        print("- questions.txt: Contains the questions")
        print("- xp.txt (optional): Tracks XP, default 0")
        print("- level.txt (optional): Tracks Level, default 1")
        print("- total_time.txt (optional): Tracks total session time, default 0")
        exit(1)

    # Check required files
    if not os.path.isfile(xp_file):
        with open(xp_file, 'w') as f:
            f.write("0")
    if not os.path.isfile(level_file):
        with open(level_file, 'w') as f:
            f.write("1")
    if not os.path.isfile(session_log):
        open(session_log, 'w').close()
    if not os.path.isfile(total_time_file):
        with open(total_time_file, 'w') as f:
            f.write("0")
    if not os.path.isfile(questions_file):
        print(f"Questions file not found: {questions_file}")
        print("Please create 'questions.txt' in the 'assets' folder.")
        exit(1)
    print(f"Assets initialized in {assets_dir}")

def display_summary(total_time_file, xp_file, level_file):
    with open(total_time_file, 'r') as f:
        total_time = int(f.read().strip())
    with open(xp_file, 'r') as f:
        xp = int(f.read().strip())
    with open(level_file, 'r') as f:
        level = int(f.read().strip())
    hours = total_time // 60
    minutes = total_time % 60
    print("Welcome to the RHEL Learning Script!")
    print(f"Total session time: {hours} hours and {minutes} minutes.")
    print(f"Current Level: {level}")
    print(f"Current XP: {xp}")
    print()
