import habit
import habit_analytics
import interface

def main():
    # Create tracker object
    tracker = habit.HabitTracker()
    # Load existing data from db
    tracker.load_habits()
    # Create background update thread
    tracker.run_tracker()
    # Start GUI
    app = interface.HabitTrackerGUI(tracker)
    app.mainloop()
    # Close database connections
    tracker.database.close_connection()
    tracker.update_database.close_connection()

if __name__ == "__main__":
    main()

#todo
# 1) implement database lock?
# 2) documentation & readability
# 3