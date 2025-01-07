def add_xp(xp_file, level_file, session_log):
    with open(xp_file, 'r') as f:
        xp = int(f.read().strip())
    with open(level_file, 'r') as f:
        level = int(f.read().strip())
    new_xp = xp + 10
    if new_xp >= level * 100:
        level += 1
        print(f"LEVEL UP! You are now Level {level}!")
        new_xp -= (level - 1) * 100
    with open(xp_file, 'w') as f:
        f.write(str(new_xp))
    with open(level_file, 'w') as f:
        f.write(str(level))
    with open(session_log, 'a') as f:
        f.write(f"XP and level updated: {new_xp} XP, Level {level}\n")
