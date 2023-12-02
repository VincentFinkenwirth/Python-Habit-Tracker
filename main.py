import habit
import habit_analytics
import interface

def main():
    tracker = habit.HabitTracker()
    tracker.load_habits()
    tracker.run_tracker()
    app = interface.HabitTrackerGUI(tracker)
    app.mainloop()
    habit_analytics.return_max_streak_string(tracker.dataframe)
    tracker.database.close_connection()
    tracker.update_database.close_connection()

if __name__ == "__main__":
    main()

#todo
# 1) implement database lock?
# 2) documentation & readability