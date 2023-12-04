import time
from datetime import datetime, timedelta
import data
import habit_analytics
import threading
import pandas as pd


class Habit:  # Habit(name, task, period, has_completed, deadline, streak, id)
    def __init__(self, name, task, period,
                 created=datetime.now(), id=None):
        # Static data
        self.name = name
        self.task = task
        self.period = period
        self.created = created
        # Dynamic data
        self.has_completed = 0
        self.deadline = created + timedelta(days=period)
        self.streak = 0
        # Assigned by database on load
        self.id = id

    def db_values(self):  # returns set of values for habit for database
        return self.name, self.task, self.period, self.created.strftime('%Y-%m-%d %H:%M:%S')

    def get_deadline(self):  # return habit deadline
        return self.deadline

    def complete(self, database):  # mark habit as complete by creating db entry
        if not self.has_completed:
            database.data_logger(self.id, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.deadline.strftime('%Y-%m-%d %H:%M:%S'))


class HabitTracker:  # main habit application
    def __init__(self, database="habit_database.db"):
        self.habits = []  # create list of active tracked habits
        self.todo = []
        # Seperate database manager for threaded and main task
        self.database = data.DatabaseManager(database)
        self.update_database = data.DatabaseManager(database)
        # Dataframe initialized
        self.dataframe = None

    def load_habits(self):  # load stored habit data from database, overwrites current.
        self.habits = []  # Reset tracked habits list
        # Load static data
        for habits in self.database.load_habits():  # Load habit data from db and loop through each entry
            self.habits.append(Habit(name=habits[1],
                                     task=habits[2],
                                     period=habits[3],
                                     created=datetime.strptime(habits[4], '%Y-%m-%d %H:%M:%S'),
                                     id=habits[0]))  # Append habit object to tracked habits list
        # Load dynamic data (deadline, streak, has_completed)
        self.load_dynamic_habit_data()

    def load_entries_dataframe(self):  # Load all entries of habit_entries database and converts them into pandas dataframe
        columns = ["habit_name", "date", "checked", "deadline"]
        df = pd.DataFrame(self.database.pull_habit_entries(), columns=columns)
        df["date"] = pd.to_datetime(df["date"])  # Format string based date into datetime
        self.dataframe = df
        self.calculate_streaks()

    def calculate_streaks(self):  # Calculate streaks of dataframe using pandas dataframe shift
        df = self.dataframe  # To improve readability of code dataframe is temporarily assigned to df
        df = df.sort_values(by=["habit_name", "date"]).copy()  # Sort the dataframe for algorithm to work

        # Create new unique key that takes habit name and checked status
        df["combined_key"] = df["habit_name"] + df["checked"].astype(str)
        # Every point of difference in the shifted dataframe marks point of new streak. Adding occ of prev changes gives streak id
        df["streak_id"] = df["combined_key"].ne(df["combined_key"].shift()).cumsum()
        # Sum up all entries with the same streak_id ,add one as cumcount starts at 0
        df["calculated_streak"] = df.groupby("streak_id").cumcount() + 1
        # Remove computation columns to clean up dataframe
        df.drop(columns=["combined_key", "streak_id"], inplace=True)
        # Update dataframe attribute
        self.dataframe = df

    def load_dynamic_habit_data(self):  # Load dynamic habit by computing on habit_entries dataframe
        # First load dataframe from database
        self.load_entries_dataframe()

        for habit in self.habits:  # Loop through all habits
            habit_dataframe = habit_analytics.filter_by_habit(self.dataframe, habit.name)
            # Check if entries for habit exist
            if len(habit_dataframe) > 0:
                # Get information from last entries
                deadline = habit_dataframe["deadline"].iloc[-1]
                deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S')
                last_completed = habit_dataframe["checked"].iloc[-1]
                # Logic to handle the different deadline scenarios
                if last_completed == 1:  # If last entry is completion
                    streak = habit_dataframe["calculated_streak"].iloc[-1]
                    if datetime.now() >= deadline:  # Check if deadline of completed entry has passed
                        deadline += timedelta(days=habit.period)  # Increment deadline by period to get new deadline
                        completed = 0  # false as "open deadline"
                    else:
                        completed = 1  # If deadline still in future, habit remains completed and deadline is last deadline
                else:  # If completion = false
                    streak = 0
                    completed = 0
                    deadline += timedelta(days=habit.period)
                # Update habit attributes
                habit.deadline = deadline
                habit.streak = streak
                habit.has_completed = completed

    def habit_exists(self, new_habit_name):  # Method to check if a habit Name already exists
        for habit in self.habits:
            if new_habit_name == habit.name:
                return True
        return False

    def get_habit(self, habit_name):  # Returns habit object with corresponding name
        for habit in self.habits:
            if habit.name == habit_name:
                return habit

    def add_habit(self, name, task, period):  # add Habit(Name, Task, Period) to tracker
        if not self.habit_exists(name):
            new = Habit(name, task, period)  # Create Habit Object
            self.database.add_habit(new.db_values())  # Add new Habit to database
            self.load_habits()  # load habit from database.

    def delete_habit(self, habit_name):  # function to remove active habit
        if self.habit_exists(habit_name):
            self.database.remove_habit(habit_name)  # Delete database entries of habit
            self.load_habits()  # Refresh habit data

    def get_habits(self):  # return list of all tracked habits
        return self.habits

    def get_habit_names(self):  # return list of tracked habit names
        return [habit.name for habit in self.habits]

    def get_deadlines(self):  # returns a dictionary of active deadlines
        temp = {}
        for habit in self.habits:
            temp[habit] = habit.get_deadline()
        return temp

    # Function to get key statistics for habits with selection parameters (list of habit_names, period, time_period)
    def get_analytics_data(self, habit_selection="All", period_selection=-1, time_period_selection=-1):
        # Create list of habits to analyze
        selected_habits = habit_analytics.tracked_habits_list(self, habit_selection, period_selection)
        # Load data from database and create dataframe
        self.load_entries_dataframe()
        # Filter by habit selection
        df = habit_analytics.filter_by_habit(self.dataframe, selected_habits)
        # Filter by cutoff_date
        df = habit_analytics.filter_by_date(df, time_period_selection)
        # Create analytics dataframe for GUI

        analytics_data, lowest_achieval = habit_analytics.analytics_data(self.habits, selected_habits, df)
        df.loc[df['checked'] == 0, 'calculated_streak'] = 0

        return analytics_data, df, lowest_achieval

# Functionality for main update loop
    def update_habits(self):  # Checks if deadline has passed and makes db entry if deadline is missed
        for habit in self.habits:
            # check if deadline passed
            while datetime.now() >= habit.deadline:
                if not habit.has_completed:  # Check if habit hasnt been completed
                    self.database.data_logger(habit.id, 0,
                                              habit.deadline.strftime('%Y-%m-%d %H:%M:%S'),
                                              habit.deadline.strftime('%Y-%m-%d %H:%M:%S'))  # Create db entry for analytics
                    self.load_dynamic_habit_data()
                else:  # Update deadline if completed and deadline passed
                    self.load_dynamic_habit_data()

    def update_habits_loop(self):  # Create loop of update function
        while True:
            self.update_habits()  # Check habits' deadlines and update if necessary
            time.sleep(60)  # Regularity of updates in sec (1min)

    def run_tracker(self):  # Create background thread of update loop that closes on completion
        habit_check_thread = threading.Thread(target=self.update_habits_loop)  # Use threading to create an update loop in background
        habit_check_thread.daemon = True  # Ensures thread with loop is closed when main program closed
        habit_check_thread.start()
