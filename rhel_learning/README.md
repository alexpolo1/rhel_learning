# rhel_learning/rhel_learning/README.md

# RHEL Learning Project

This project is a Python-based learning tool designed to help users enhance their knowledge of Red Hat Enterprise Linux (RHEL). It includes a session management system, XP tracking, and a question-and-answer format to facilitate learning.

## Project Structure

```
rhel_learning
├── src
│   ├── main.py                # Entry point of the application
│   ├── assets
│   │   ├── xp.txt             # Tracks XP earned during sessions
│   │   ├── level.txt          # Tracks the current level of the user
│   │   ├── session.log         # Logs session start and end times
│   │   ├── questions.txt       # Contains questions for learning sessions
│   │   └── total_time.txt      # Tracks total session time
│   ├── utils
│   │   ├── __init__.py        # Marks the utils directory as a package
│   │   ├── assets.py           # Functions for managing asset files
│   │   ├── session.py          # Functions for logging sessions
│   │   ├── steam.py            # Functions for managing Steam processes
│   │   ├── timer.py            # Functions for running the session timer
│   │   └── xp.py               # Functions for managing XP and level-ups
├── requirements.txt            # Lists dependencies for the project
└── README.md                   # Documentation for the project
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd rhel_learning
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure that the `assets` directory contains the necessary files:
   - `questions.txt`: Contains the questions for the learning sessions.
   - `xp.txt`: Initialized to 0 if not present.
   - `level.txt`: Initialized to 1 if not present.
   - `total_time.txt`: Initialized to 0 if not present.

## Usage

To start the learning session, run the following command:
```
python src/main.py
```

This will initialize the assets, log the session start, display the session summary, start the timer, and manage the XP and level-up system.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.