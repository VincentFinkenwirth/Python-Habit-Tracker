import sqlite3

class DatabaseManager:  # Class that connects to a database(creates file if not exists)
    def __init__(self, database = "habit_database.db"):
        self.conn = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_Tables()
        #self.lock = threading.Lock()

    def create_Tables(self):  # Function to create tables if none exist
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS habits("
            "habit_id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "habit_name TEXT NOT NULL, "
            "task TEXT, "
            "period INTEGER NOT NULL, "
            "date_created DATETIME NOT NULL)"
        )
        self.conn.commit()

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS habit_entries("
            "id_entry INTEGER PRIMARY KEY AUTOINCREMENT, "
            "habit_id INTEGER NOT NULL, "
            "checked INTEGER NOT NULL, "
            "date DATETIME NOT NULL, "
            "deadline DATETIME NOT NULL, "
            "FOREIGN KEY (habit_id) REFERENCES habits(habit_id) ON DELETE CASCADE)")
        self.conn.commit()

    def add_habit(self, habit_db_values):  # Static database entry for habit
        add_query = "INSERT INTO habits (habit_name, task, period, date_created) VALUES (?, ?, ?, ?)"
        self.cursor.execute(add_query, habit_db_values)
        self.conn.commit()

    def load_habits(self):  # Load static data from db (Name, Task, Period, Date_created ID)
        load_query = "SELECT * FROM habits"
        self.cursor.execute(load_query)
        return self.cursor.fetchall()

    def remove_habit(self, habit_name):  # Delete habit_name from db
        delete_query = f"DELETE FROM habits WHERE habit_name = '{habit_name}'"
        self.cursor.execute(delete_query)
        self.conn.commit()

    def update_habit(self, task, period, habit_id):  # For future usage, not yet used
        update_query = "UPDATE habits SET task = ?, period = ? WHERE habit_id = ?"
        self.cursor.execute(update_query, (task, period, habit_id))
        self.conn.commit()

    def data_logger(self, habit_id, checked, date, deadline):  # Create dynamic habit entry ( Habit_id, checked, date, deadline)
        data_query = "INSERT INTO habit_entries (habit_id, checked, date, deadline) VALUES (?, ?, ?, ?)"
        self.cursor.execute(data_query, (habit_id, checked, date, deadline))
        self.conn.commit()

    def pull_habit_entries(self):  # Load all dynamic entries from habit_entries table
        pull_query = ("SELECT habits.habit_name AS habit_name, habit_entries.date, habit_entries.checked, habit_entries.deadline "
                      "FROM habit_entries "
                      "INNER JOIN habits ON habit_entries.habit_id = habits.habit_id")
        self.cursor.execute(pull_query)
        return self.cursor.fetchall()

    def close_connection(self):  # Close connection and cursor
        self.cursor.close()
        self.conn.close()