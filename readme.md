# Habit Tracker application using tkinter

Simple habit tracker designed to keep track and analyze important habits.


## WIP
## Requirements
[Python](https://www.python.org/) >= 3.9

## External Modules
- pandas
- seaborn
- matplotlib

## Installation
Clone depository
```bash
 git clone https://github.com/VincentFinkenwirth/Python-Habit-Tracker.git
```
Create virtualenv:
```bash
python -m venv env
```
Navigate to project directory:
```bash
cd Python-Habit-Tracker
```
Install dependencies:
```bash
pip install -r requirements.txt
```

Run:
```bash
python main.py
```

## Features

![Add/delete](images/add_delete.png)

- Add new habits you want to track.
- Delete habits from tracker.

![Tracked](images/tracked_analytics.png)

- Track, complete and gain streaks.
- View analytics and reflect.
- Basic fluent tkinter GUI for easy handling.
- local file sql database

## Test
```bash
python tracker_unittest.py
```

## License

This project is licensed under the [MIT License](LICENSE).