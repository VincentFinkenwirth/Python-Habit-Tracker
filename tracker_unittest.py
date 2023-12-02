import unittest
from datetime import datetime, timedelta
import habit_analytics
import sampleData
import habit
import os

class TestHabitTracker(unittest.TestCase):
    def setUp(self):
        # Create tracker with its own Test database
        self.tracker = habit.HabitTracker("UnitTest_Habit_database.db")

    def test_habit_exists(self):
        # Add habit to tracker using append
        hbit = habit.Habit("Exercise", "Gym", 7)
        self.tracker.habits.append(hbit)

        # Test if habit exists:
        self.assertTrue(self.tracker.habit_exists("Exercise"))
        self.assertFalse(self.tracker.habit_exists("Read"))

    def test_add_habit(self):  # Use habit_exists method for this test
        self.tracker.habits = []
        # Test simple case of adding a habit
        self.tracker.add_habit("Read", "Books", 1)
        self.assertTrue(self.tracker.habit_exists("Read"))

        # Test to not add duplicates
        length = len(self.tracker.habits)
        self.tracker.add_habit("Read", "Books", 1)
        # Check if length of list is the same
        self.assertEqual(length, len(self.tracker.habits))

    def test_load_habit(self):
        # Add habit
        self.tracker.add_habit("Read", "Books", 1)
        self.tracker.add_habit("Swim", "Sea", 1)
        # Check if habit delete gets also deleted from db
        self.tracker.delete_habit("Swim")
        # Clear habit list
        self.tracker.habits = []
        # Load habit from database
        self.tracker.load_habits()
        # Check if Habit is in list
        self.assertTrue(self.tracker.habit_exists("Read"))
        self.assertFalse(self.tracker.habit_exists("Swim"))

    def test_get_habit_names(self):
        self.tracker.add_habit("Read", "Books", 1)
        self.tracker.add_habit("Swim", "Sea", 1)

        name_list = self.tracker.get_habit_names()
        self.assertEqual(name_list, ["Read", "Swim"])

    def test_delete_habit(self):
        self.tracker.delete_habit("Read")
        self.tracker.delete_habit("Swim")

        self.tracker.load_habits()

        self.assertFalse(self.tracker.habit_exists("Read"))
        self.assertFalse(self.tracker.habit_exists("Swim"))

    # Now testing the more complicated dynamic data
    # This test uses the sampleData module, that contains a number of habits with entries.
    # SampleData also contains a dict of manually calculated expected values for each habit.

    def test_on_sample_data(self):
        # Create sample habits
        if sampleData.create_test_habits(self.tracker):
            sampleData.create_habit_entries(self.tracker)

        # Load solutions
        solutions = sampleData.streak_cheat

        # Load dynamic data from database
        self.tracker.load_dynamic_habit_data()

        # loop through all sample habits
        for habit in self.tracker.habits:
            # Unpack expected values from SampleData solution
            longest, current, sum_achieved, total = solutions[habit.name]

            # As current streak gets calculated on load it is a simple test.
            self.assertEqual(habit.streak, current)

            # Calculate max streak using habit_analytics module
            calculated_longest = habit_analytics.get_max_streak(self.tracker. dataframe, habit.name)

            self.assertEqual(longest, calculated_longest)

            # Calculate achieval data using habit_analytics
            calculated_achieved, calculated_total, _ = habit_analytics.return_achieval_rate(self.tracker.dataframe, habit.name)

            self.assertEqual(calculated_achieved, sum_achieved)
            self.assertEqual(calculated_total, total)

        # Test filter for periodicy (only weekly as method is the same for daily)

        self.tracker.load_habits()
        tracker_weekly = set(habit_analytics.tracked_habits_list(self.tracker, "All", 7))
        # Expected results
        weekly = {"Learn Spanish", "Healthy Eating", "Blogging"}
        # Test
        self.assertEqual(tracker_weekly, weekly)

    # Test for correct deadline calculation, update and complete functionality
    def test_dynamic_functionalities(self):
        # Create test habit
        date_created = datetime.now() - timedelta(days=3)
        self.tracker.database.add_habit(("Test1", "Test", 1, date_created.strftime('%Y-%m-%d %H:%M:%S')))
        # load ID from database
        self.tracker.load_habits()

        # Deadline should be date created + period(1)
        deadline = date_created + timedelta(days=1)

        # Load our test habit.
        Test1 = self.tracker.get_habit("Test1")
        # Test if calculated deadline is correct
        self.assertEqual(Test1.deadline.strftime('%Y-%m-%d %H:%M:%S'), deadline.strftime('%Y-%m-%d %H:%M:%S'))

        # Create habit entry to simulate event of missed/broken deadline
        self.tracker.database.data_logger(Test1.id, 0, deadline.strftime('%Y-%m-%d %H:%M:%S'), deadline.strftime('%Y-%m-%d %H:%M:%S'))

        # Compute data
        self.tracker.load_habits()
        # Load Test1 habit
        Test1 = self.tracker.get_habit("Test1")

        # New deadline should again be shifted by a period(1)
        deadline += timedelta(days=1)
        # Test if new deadline is correct
        self.assertEqual(deadline.strftime('%Y-%m-%d %H:%M:%S'), Test1.deadline.strftime('%Y-%m-%d %H:%M:%S'))

        # Test update function, which should create 2 entries for the "missed days"
        self.tracker.update_habits()
        # Load habit data
        Test1 = self.tracker.get_habit("Test1")
        # Deadline should be shifted by 2 days
        deadline += timedelta(days=2)  # update function should have createed 2 entrys which shifts deadlinee by 2 days

        self.assertEqual(deadline.strftime('%Y-%m-%d %H:%M:%S'), Test1.deadline.strftime('%Y-%m-%d %H:%M:%S'))

        # Now test completion method. As deadline is in future, it should remain unchanged.
        Test1.complete(self.tracker.database)
        # Compute data
        self.tracker.load_habits()
        Test1 = self.tracker.get_habit("Test1")
        # Check if streak has increased to 1 from 0 (this should confirm habit has been checked)
        self.assertEqual(Test1.streak, 1)
        # Check if dhas_completed turns true
        self.assertEqual(Test1.has_completed, 1)
        # Check if deadline remains unchanged
        self.assertEqual(deadline.strftime('%Y-%m-%d %H:%M:%S'), Test1.deadline.strftime('%Y-%m-%d %H:%M:%S'))

    def tearDown(self):
        self.tracker.database.close_connection()
        self.tracker.update_database.close_connection()
        if os.path.exists("UnitTest_Habit_database.db"):
            os.remove("UnitTest_Habit_database.db")


def delete_test_database():
    if os.path.exists("UnitTest_Habit_database.db"):
            os.remove("UnitTest_Habit_database.db")



if __name__ == '__main__':
    unittest.main()
    delete_test_database()
