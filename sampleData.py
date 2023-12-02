from datetime import datetime, timedelta
import random

#  List of sample habits
test_habits = [
    ("Workout", "Exercise, not just on Jan 02", 1),
    ("Read", "Reading Books is never old fashioned!", 1),
    ("Meditate", "Clan mind", 1),
    ("Water", "Stay Hydrated", 1),
    ("Coding Practice", "Programming a habit tracker", 1),
    ("Blogging", "Writing about trends", 7),
    ("Healthy Eating", "Gotta eat healthy at least once a week", 7),
    ("Learn Spanish", "Buenas dias", 7)
]
habit_entries = {
    "Workout" : [1,0,0,1,1,1,1,1,1,0,0,0,0,1,1,1,0,1,1,0,0,1,1,1,1],
    "Read" : [0,1,1,1,1,1,1,0,1,0,1,0,1,1,1,1,1,0,0,0,0,0,0,1,0],
    "Meditate" : [0,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
    "Water" : [1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1],
    "Coding Practice" : [0,1,1,1,0,0,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    "Blogging" : [0,0,0,0,0,0],
    "Healthy Eating" : [1,0,1,1,1,1],
    "Learn Spanish" : [0,1,0,1,0,1]
}

streak_cheat = {  # habit :[longest, current streak, sum_completed, total_entries]  (Used for test case-manually calculated)
    "Workout" : [6, 4, 16, 25],
    "Read" : [6, 0, 14, 25],
    "Meditate" : [1, 1, 3, 15],
    "Water" : [14, 5, 19, 20],
    "Coding Practice" : [15, 15, 19, 24],
    "Blogging" : [0, 0, 0, 6],
    "Healthy Eating" : [4, 4, 5, 6],
    "Learn Spanish" : [1, 1, 3, 6]
}


def create_test_habits(tracker):
    # Add habits to tracker habit_name, task, period, date_created, has_completed, deadline, current_streak
    if not tracker.habits:
        for habit_name, task, period in test_habits:
            date_created = datetime.now()- timedelta(len(habit_entries[habit_name])*period) + timedelta(minutes=1)
            date_created = date_created.strftime('%Y-%m-%d %H:%M:%S')
            tracker.database.add_habit((habit_name, task, period, date_created))
        return True

def create_habit_entries(tracker):  # Use before tracker.run
    tracker.load_habits()
    # Loop through each habit
    test_habits = tracker.habits
    for habit in test_habits:
        entries = habit_entries[habit.name]
        for index, entry in enumerate(entries):
            deadline = habit.created + timedelta(days=((index+1)*habit.period))
            date = deadline - timedelta(hours=random.randint(1,22))
            deadline.strftime('%Y-%m-%d %H:%M:%S')
            date.strftime('%Y-%m-%d %H:%M:%S')
            # habit_id, checked, date, deadline
            tracker.database.data_logger(habit.id, entry, date,deadline)
    # Load dynamic habit data
    tracker.load_habits()