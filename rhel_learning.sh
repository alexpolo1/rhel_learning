#!/bin/bash

# Variables
SCRIPT_DIR=$(dirname "$(realpath "$0")")
ASSETS_DIR="$SCRIPT_DIR/assets"
XP_FILE="$ASSETS_DIR/xp.txt"
LEVEL_FILE="$ASSETS_DIR/level.txt"
SESSION_LOG="$ASSETS_DIR/session.log"
QUESTIONS_FILE="$ASSETS_DIR/questions.txt"
TOTAL_TIME_FILE="$ASSETS_DIR/total_time.txt"
URL="https://rol.redhat.com"
TIMER_MINUTES=20

# Ensure assets directory and files exist
initialize_assets() {
    if [ ! -d "$ASSETS_DIR" ]; then
        echo "Assets directory not found: $ASSETS_DIR"
        echo "Please create the 'assets' folder and include the required files:"
        echo "- questions.txt: Contains the questions"
        echo "- xp.txt (optional): Tracks XP, default 0"
        echo "- level.txt (optional): Tracks Level, default 1"
        echo "- total_time.txt (optional): Tracks total session time, default 0"
        exit 1
    fi

    # Check required files
    [ ! -f "$XP_FILE" ] && echo "0" > "$XP_FILE"
    [ ! -f "$LEVEL_FILE" ] && echo "1" > "$LEVEL_FILE"
    [ ! -f "$SESSION_LOG" ] && touch "$SESSION_LOG"
    [ ! -f "$TOTAL_TIME_FILE" ] && echo "0" > "$TOTAL_TIME_FILE"
    if [ ! -f "$QUESTIONS_FILE" ]; then
        echo "Questions file not found: $QUESTIONS_FILE"
        echo "Please create 'questions.txt' in the 'assets' folder."
        exit 1
    fi
    echo "Assets initialized in $ASSETS_DIR"
}

# Log session start and end
log_session() {
    local action=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    if [ "$action" == "start" ]; then
        echo "Session started: $timestamp" >> "$SESSION_LOG"
    elif [ "$action" == "end" ]; then
        echo "Session ended: $timestamp, Duration: $TIMER_MINUTES minutes" >> "$SESSION_LOG"
    fi
}

# Display session summary
display_summary() {
    local total_time=$(cat "$TOTAL_TIME_FILE")
    local xp=$(cat "$XP_FILE")
    local level=$(cat "$LEVEL_FILE")
    local hours=$((total_time / 60))
    local minutes=$((total_time % 60))
    echo "Welcome to the RHEL Learning Script!"
    echo "Total session time: $hours hours and $minutes minutes."
    echo "Current Level: $level"
    echo "Current XP: $xp"
    echo
}

# Function to kill Steam processes
kill_steam() {
    while true; do
        steam_pids=$(ps aux | grep steam | grep -v grep | awk '{print $2}')
        if [ -n "$steam_pids" ]; then
            echo "Killing Steam processes..."
            sudo /bin/kill -9 $steam_pids || echo "Failed to kill Steam processes"
        fi
        sleep 5  # Check every 5 seconds
    done
}

# Timer function with window focus
show_timer() {
    echo "The session will last $TIMER_MINUTES minutes."

    # Open the URL in Chromium
    if [ -n "$DISPLAY" ]; then
        chromium "$URL" >/dev/null 2>&1 &
        sleep 2  # Allow the browser to open
        wmctrl -r ":ACTIVE:" -b add,above
    else
        echo "No graphical environment detected. Skipping browser opening."
    fi

    # Open a new terminal window and run the secondary script
    gnome-terminal -- bash -c "$SCRIPT_DIR/timer_and_questions.sh $TIMER_MINUTES $QUESTIONS_FILE $SESSION_LOG; exec bash"

    # Add session time to total
    local total_time=$(cat "$TOTAL_TIME_FILE")
    total_time=$((total_time + TIMER_MINUTES))
    echo "$total_time" > "$TOTAL_TIME_FILE"
}

# XP and level-up system
add_xp() {
    local xp=$(cat "$XP_FILE")
    local level=$(cat "$LEVEL_FILE")
    local new_xp=$((xp + 10))
    if ((new_xp >= level * 100)); then
        level=$((level + 1))
        echo "LEVEL UP! You are now Level $level!"
        new_xp=$((new_xp - (level - 1) * 100))
    fi
    echo "$new_xp" > "$XP_FILE"
    echo "$level" > "$LEVEL_FILE"
    echo "XP and level updated: $new_xp XP, Level $level" >> "$SESSION_LOG"
}

# Handle script interruption
trap 'echo "Script interrupted. Cleaning up..."; kill $STEAM_KILL_PID; wmctrl -r ":ACTIVE:" -b remove,above; exit 1' INT TERM

# Initialize assets
initialize_assets

# Log session start
log_session "start"

# Display session summary
display_summary

# Start killing Steam processes in the background
kill_steam &
STEAM_KILL_PID=$!

# Start session
echo "Starting RHEL Learning Session..."
show_timer

# Add XP
add_xp

# Stop killing Steam processes
kill $STEAM_KILL_PID

# Log session end
log_session "end"

