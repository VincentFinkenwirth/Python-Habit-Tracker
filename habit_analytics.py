from datetime import datetime, timedelta

def filter_by_period(habits, period):  # Return a list of habit names of a given period
    if period > 0:
        filter = [habit.name for habit in habits if habit.period == period]
        return  filter
    return habits

def filter_by_date(dataframe, num_days):  # Function to create a DataFrame only containing values within the last num_days days
    if num_days > 0:
        cutoff_date = datetime.now() - timedelta(days = num_days)
        return dataframe[dataframe["date"] >= cutoff_date]
    return dataframe

def tracked_habits_list(tracker, habit_selection="All", period_selection=-1):  # Function to get list of habit names to analyze
    if habit_selection == "All" and period_selection < 0:
        return tracker.get_habit_names()
    elif habit_selection == "All":
        return filter_by_period(tracker.habits, period_selection)
    else:
        return [habit_selection]
def filter_by_habit(dataframe, habit_names):
    if not isinstance(habit_names, list):
        habit_names = [habit_names]
    return dataframe[dataframe["habit_name"].isin(habit_names)]

def return_achieval_rate(dataframe, habit_name=None):  # Function to return (completed, total, rate) of checked entries in dataframe
    # Filters dataframe if a single habit is selected
    if habit_name:
        dataframe = dataframe[dataframe["habit_name"] == habit_name]
    # Use loc to only look at completed entries and sum up to get number of completed
    completed = dataframe.loc[dataframe["checked"] == 1, "checked"].count()
    total = len(dataframe)
    # Error handling to prevent division by 0
    if total > 0:
        rate = completed/total*100
    else:
        rate = 0
    return (completed, total, rate)

def get_max_streak(dataframe, habit_name=None):
    if habit_name:
        dataframe = dataframe[dataframe["habit_name"] == habit_name]
    dataframe = dataframe[dataframe["checked"] == 1]
    if len(dataframe)>0:
        return dataframe["calculated_streak"].max()
    return 0

def return_max_streak_string(dataframe):  # Returns the longest streak and corresponding habit in a string
    dataframe = dataframe[dataframe["checked"] == 1]
    if len(dataframe)>0:
        index = dataframe["calculated_streak"].idxmax()
        habit_name = dataframe.loc[index, "habit_name"]
        longest_streak = dataframe.loc[index, "calculated_streak"]
        return f"The overall longest streak is {longest_streak}, achieved in {habit_name}"

def analytics_data(habits, habit_selection, dataframe):
    analytics_data = []
    lowest_achieval = (200, "")

    for habit in habit_selection:  # Create entries for each selected habit
        current_streak = [hbit.streak for hbit in habits if hbit.name==habit]
        longest_streak = get_max_streak(dataframe, habit)
        completed, total, rate = return_achieval_rate(dataframe, habit)
        #  Keep track of habit with lowest achieval rate
        if rate < lowest_achieval[0]:
            lowest_achieval = (rate, habit)
        # Append data to list
        analytics_data.append((habit, current_streak, longest_streak, completed, total, f"{int(rate)}%"))

        # Total data:
    longest_streak = get_max_streak(dataframe)
    completed, total, rate = return_achieval_rate(dataframe)
    if rate == None:
            rate = 0
    # Append total
    analytics_data.append(("Total","", longest_streak, completed, total, f"{int(rate)}%"))

    return analytics_data, lowest_achieval