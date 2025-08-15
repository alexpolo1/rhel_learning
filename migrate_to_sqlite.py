import os
from datetime import datetime
from main import (
    XP_FILE, LEVEL_FILE, TOTAL_TIME_FILE, SESSION_LOG, DB_PATH, SUBSCRIPTION_END_DATE, UserStatsSqlite
)

def migrate_txt_to_sqlite():
    migrated = False
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
    if migrated:
        stats = UserStatsSqlite(DB_PATH, SUBSCRIPTION_END_DATE)
        stats.save_stats(xp, level, total_time)
    if os.path.exists(SESSION_LOG):
        stats = UserStatsSqlite(DB_PATH, SUBSCRIPTION_END_DATE)
        try:
            with open(SESSION_LOG) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        import re
                        m = re.match(r'Session (\w+): (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                        if m:
                            status, timestamp = m.groups()
                            stats.log_session(status, duration=None)
        except Exception:
            pass
        migrated = True
    if migrated:
        for f in [XP_FILE, LEVEL_FILE, TOTAL_TIME_FILE, SESSION_LOG]:
            try:
                os.remove(f)
            except Exception:
                pass
    if migrated:
        print("Migration complete. Data moved to SQLite and text files removed.")
    else:
        print("No migration needed. No text files found.")

if __name__ == "__main__":
    migrate_txt_to_sqlite()
