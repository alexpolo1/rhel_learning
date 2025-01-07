from datetime import datetime

def log_session(session_log, action):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(session_log, 'a') as f:
        if action == "start":
            f.write(f"Session started: {timestamp}\n")
        elif action == "end":
            f.write(f"Session ended: {timestamp}, Duration: 20 minutes\n")
