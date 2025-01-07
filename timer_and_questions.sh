#!/bin/bash

TIMER_MINUTES=$1
QUESTIONS_FILE=$2
SESSION_LOG=$3

# Timer function
run_timer() {
    local seconds=$((TIMER_MINUTES * 60))
    for ((i = 1; i <= seconds; i++)); do
        echo -ne "Time remaining: $((seconds - i)) seconds\r"
        sleep 1
    done
    echo -e "\nSession complete!"
}

# Function to display a random question
ask_random_question() {
    mapfile -t questions < "$QUESTIONS_FILE"
    local random_index=$((RANDOM % ${#questions[@]}))
    IFS='|' read -r question opt1 opt2 opt3 correct <<<"${questions[random_index]}"
    echo "$question"
    echo "1. $opt1"
    echo "2. $opt2"
    echo "3. $opt3"
    local answer
    read -p "Choose an answer (1-3): " answer
    if [ "$answer" -eq "$correct" ]; then
        echo "Correct answer!"
        echo "$question|Correct" >> "$SESSION_LOG"
    else
        echo "Wrong answer. The correct option was: $correct"
        echo "$question|Wrong" >> "$SESSION_LOG"
    fi
}

# Run the timer
run_timer

# Ask a random question
ask_random_question

# Wait for user input to close the terminal
read -p "Press Enter to close..."
