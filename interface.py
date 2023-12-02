import tkinter as tk
import tkinter.messagebox
from tkinter import ttk
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import habit_analytics


class HabitTrackerGUI(tk.Tk):  # GUI class
    def __init__(self, HabitTracker):
        super().__init__()
        # Design
        self.title("Habit Tracker")
        self.geometry("300x500")
        self.main_menu()
        # Functionality(backend)
        self.HabitTracker = HabitTracker
        # Selection parameters
        self.periods = ["Daily", "Weekly", "Monthly", "All"]
        self.period_to_int = {"Daily": 1, "Weekly": 7, "Monthly": 31, "All": -1}
        self.int_to_period = {1: "Daily", 7: "Weekly", 31: "Monthly", -1: "All"}

        self.time_periods = ["Last 7 days", "Last 30 days", "Last 90 days", "All time"]
        self.time_periods_to_int = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90, "All time": -1}

#########################################Main Menu#################################################
    def main_menu(self):  # function that creates the main window
        button_style = {
            "font": ("Arial", 12),
            "width": 20,
            "height": 4,
            "bd": 3,
            "bg": "#45a049",  # Green color
            "fg": "white",
            "activebackground": "#45a049",  # Darker green color on hover
            "activeforeground": "white"
        }

        self.label = tk.Label(self, text="Habit Tracker")
        self.label.pack()
        # Add Habit Button
        self.add_habit_button = tk.Button(self, text="Add Habit", command=self.show_add_habit_window, **button_style)
        self.add_habit_button.pack()
        # Remove habit button
        self.delete_habit_button = tk.Button(self, text="Delete Habit", command = self.show_delete_habit_window, **button_style)
        self.delete_habit_button.pack()
        # Tracked habit button
        self.show_tracked_habits_button = tk.Button(self, text="Current Todo", command = self.show_tracked_habits, **button_style)
        self.show_tracked_habits_button.pack()
        # Analytics Button
        self.analytics_button = tk.Button(self, text="Analytics", command=self.show_analytics_settings, **button_style)
        self.analytics_button.pack()
        # Quit application button
        self.quit_button = tk.Button(self, text="Quit", command=self.quit, **button_style)
        self.quit_button.pack()

#########################################Add habit#################################################
    def show_add_habit_window(self):  # function that creates a pop up for a new habit entry
        # Function to get user input and handle logic of add habit
        def add_habit_to_tracker():
            name = name_entry.get()
            task = task_entry.get()
            period = period_entry.get()  # Convert period from string to int

            if name and task and period:
                if not self.HabitTracker.habit_exists(name):
                    self.HabitTracker.add_habit(name, task, self.period_to_int[period])
                    add_window.destroy()  # Close the Toplevel window after adding the habit
                    tkinter.messagebox.showinfo("Success!",f"{period} habit {name}-{task} added to tracker. Lets get going!")
                else:
                    tk.messagebox.showerror("Error!", f"Habit {name} already exists, please be more specific!")
            else:
                print("Plese enter valid arguments!")

        add_window = tk.Toplevel(self)
        add_window.title("Add New Habit")
        # Labels and Entry widgets for habit information
        name_label = tk.Label(add_window, text="Habit Name:")
        name_label.grid(row=0, column=0)
        name_entry = tk.Entry(add_window)
        name_entry.grid(row=0, column=1)

        task_label = tk.Label(add_window, text="Habit Task:")
        task_label.grid(row=1, column=0)
        task_entry = tk.Entry(add_window)
        task_entry.grid(row=1, column=1)

        periods = ["Daily", "Weekly", "Monthly"]
        period_label = tk.Label(add_window, text="Habit Period (in days):")
        period_label.grid(row=2, column=0)

        period_entry = tk.StringVar(add_window)
        period_dropdown = tk.OptionMenu(add_window, period_entry, *periods)

        period_dropdown.grid(row=2, column=1)


        # Button to confirm habit addition
        add_button = tk.Button(add_window, text="Add Habit", command=add_habit_to_tracker)
        add_button.grid(row=3, column=1)
        # Close window
        back_to_menu_button = tk.Button(add_window, text="Back to Menu",command=add_window.destroy)
        back_to_menu_button.grid(row=3, column=0)

    #########################################Delete habit#################################################
    def show_delete_habit_window(self):
        # Function to handle habit deletion
        def delete_habit_from_tracker():
            name = selected_habit.get()
            if name and tkinter.messagebox.askokcancel("Delete habit", f"Are you sur you want to delete habit: {name}"):
                self.HabitTracker.delete_habit(name)
                tkinter.messagebox.showinfo("Deleted!", f"Habit '{name}' Deleted")
                delete_window.destroy()
                self.show_delete_habit_window()
            else:
                print(f"Please select a habit")

        delete_window = tk.Toplevel(self)
        delete_window.title("Delete Habit")

        if self.HabitTracker.get_habit_names():  # Check if any habits exist
            selected_habit = tk.StringVar(delete_window)  # variable for chosen habit
            delete_label = tk.Label(delete_window, text="Enter Habit Name to Delete:")
            delete_label.grid(row=0, column=0)
            # Dropdown containing all tracked habits
            delete_dropdown = tk.OptionMenu(delete_window, selected_habit, *self.HabitTracker.get_habit_names())
            delete_dropdown.grid(row=0, column =1)
            # Button to execute habit deletion
            delete_button = tk.Button(delete_window, text="Delete Habit", command=delete_habit_from_tracker)
            delete_button.grid(row=1, column=1)
        else:
            delete_label = tk.Label(delete_window, text="You currently don´t track any habits!")
            delete_label.grid(row=0, column=0)

        back_to_menu_button = tk.Button(delete_window, text="Back to Menu",command=delete_window.destroy)
        back_to_menu_button.grid(row=1, column = 0)

    #########################################Tracked habits#################################################
    def show_tracked_habits(self):
        # Create new window
        tracked_habits_window = tk.Toplevel(self)
        tracked_habits_window.geometry("1000x400")
        tracked_habits_window.title("Tracked Habits")

        # Load a sorted list of tracked habits by deadline
        tracked_habits = sorted(self.HabitTracker.get_habits(), key=lambda habit: habit.get_deadline())
# Create tracked habits treeview with task, deadline, streak and completion
        tree = ttk.Treeview(tracked_habits_window)
        tree["columns"] = ("Task", "Period", "Deadline", "Streak", "Completion")
        tree.column("#0", width=200)
        tree.column("Task", width=150, anchor="e")
        tree.column("Period", width=70, anchor="e")
        tree.column("Deadline", width=100, anchor="e")
        tree.column("Streak", width=70, anchor="e")
        tree.column("Completion", width=100, anchor="e")

        tree.heading("#0", text="Habit")
        tree.heading("Task", text="Task")
        tree.heading("Period", text="Period")
        tree.heading("Deadline", text="Deadline")
        tree.heading("Streak", text="Streak")
        tree.heading("Completion", text="Completion")
        # Create entries for each habits
        row = 0  # Used for keeping track of where to place complete_habit button

        for habit in tracked_habits:
            tree.insert("", "end", text=habit.name, values=(habit.task, self.int_to_period[habit.period],
                habit.get_deadline().strftime('%d.%m.%Y %H:%M'), habit.streak, "Completed" if habit.has_completed else ""))
            if not habit.has_completed:
                complete_button = tk.Button(tracked_habits_window, text="Complete", borderwidth = 3, command=lambda h=habit: self.mark_as_completed(h, self.HabitTracker.database, tracked_habits_window))
                complete_button.place(relx=0.8, y= 23+row*20, relwidth=0.2, height=20)
            row+=1

        tree.place(relx=0.0, rely=0.0, relwidth=0.8, relheight=1.0)

        back_to_menu_button = tk.Button(tracked_habits_window, text="Back to Menu", command=tracked_habits_window.destroy)
        back_to_menu_button.place(relx=0.5, rely=1.0, anchor="s")

    def mark_as_completed(self, habit, database, window):
        habit.complete(database)
        self.HabitTracker.load_dynamic_habit_data()
        window.destroy()
        self.show_tracked_habits()

    #########################################Analytics#################################################
    def show_analytics_settings(self):
        analytics_settings_window = tk.Toplevel(self)
        analytics_settings_window.geometry("350x200")
        analytics_settings_window.title("Analytics")

# Select specific habit
        habit_dropdown_label = tk.Label(analytics_settings_window, text="Select Habit:")
        habit_dropdown_label.place(relx=0.1, rely=0)
        # Create variable for selected habits, default to "all"
        selected_habit = tk.StringVar()
        selected_habit.set("All")
        # Create List of options for habits
        habit_dropdown_options = ["All"] + self.HabitTracker.get_habit_names()
        # Create dropdown to select habit
        habit_dropdown = tk.OptionMenu(analytics_settings_window, selected_habit, *habit_dropdown_options)
        habit_dropdown.config(width=15)
        habit_dropdown.place(relx=0.6, rely=0)
# Select Time Period
        selected_time_period = tk.StringVar()
        selected_time_period.set("All time")  # Set the default period
# Create Dropdown for periods
        time_period_dropdown_label = tk.Label(analytics_settings_window, text="Select Time:")
        time_period_dropdown_label.place(relx=0.1, rely=0.2)
        time_period_dropdown = tk.OptionMenu(analytics_settings_window, selected_time_period, *self.time_periods)
        time_period_dropdown.config(width=15)
        time_period_dropdown.place(relx=0.6, rely=0.2)
# Select Periodicy of habit
        selected_period = tk.StringVar()
        selected_period.set("All")
# Create Dropdown for periodicy
        periodicy_dropdown_label = tk.Label(analytics_settings_window, text="Select Period:")
        periodicy_dropdown_label.place(relx=0.1, rely=0.4)
        periodicy_dropdown = tk.OptionMenu(analytics_settings_window, selected_period, *self.periods)
        periodicy_dropdown.config(width=15)
        periodicy_dropdown.place(relx=0.6, rely=0.4)
#Load Data Button
        load_data_button = tk.Button(analytics_settings_window, text="Load Data", command=lambda: self.show_analytics_data(analytics_settings_window, selected_habit, selected_time_period, selected_period))
        load_data_button.place(relx=0.6, rely=0.6)
# Back to menu Button
        back_to_menu_button = tk.Button(analytics_settings_window, text="Back to Menu",command=analytics_settings_window.destroy)
        back_to_menu_button.place(relx=0.6, rely=0.8)


    def show_analytics_data(self, window, selected_habit, selected_time_period, selected_periodicity):
        analytics_data_window = tk.Toplevel(self)
        analytics_data_window.geometry("600x400")
        analytics_data_window.title("Analytics")

        # Create a Treeview with Habit, Current streak, Longest streak, Achieval
        tree = ttk.Treeview(analytics_data_window,
                            columns=("Current Streak", "Longest Streak", "Completed/Total", "Rate"))

        tree.heading("#0", text="Habit")
        tree.heading("#1", text="Current Streak")
        tree.heading("#2", text="Longest Streak")
        tree.heading("#3", text="Completed/Total")
        tree.heading("#4", text="Rate")
        tree.column("#0", width=150, anchor='w')  # Habit column
        tree.column("#1", width=50, anchor='e')  # Longest Streak column
        tree.column("#2", width=50, anchor='e')  # Current Streak column
        tree.column("#3", width=100, anchor='e')  # Achieval column
        tree.column("#4", width=50, anchor='e')  # Rate column

        # Get parameter selection
        selected_habit = selected_habit.get()
        selected_time_period = self.time_periods_to_int[selected_time_period.get()]
        selected_period = self.period_to_int[selected_periodicity.get()]

        # Load data based on selection
        analytics_data, graph_df, lowest_achieval = self.HabitTracker.get_analytics_data(selected_habit,selected_period,selected_time_period)

        # Create entries for selected habits ((0)habit_name, (1)current_streak, (2)longest_streak, (3)completed, (4)total)
        if len(analytics_data)>0:
            for entry in analytics_data:
                acieval = f"{entry[3]}/{entry[4]}"
                tree.insert("", "end", text = entry[0], values=(entry[1],entry[2], acieval, entry[5]))

        tree.grid()
        # Display some nice to know facts
        if len(analytics_data)>2:  # Only display if multiple habits selected
            # Reminder of worst achieved habit
            lowest_achieval_label = tk.Label(analytics_data_window,
                            text=f"Try spending more time on {lowest_achieval[1]} "
                            f"as you only managed to complete it {int(lowest_achieval[0])}% of times.")
            lowest_achieval_label.grid()
            # Longest streak habit

            longest_streak_label = tk.Label(analytics_data_window, text=habit_analytics.return_max_streak_string(graph_df))
            longest_streak_label.grid()


        back_to_menu_button = tk.Button(analytics_data_window, text="Back to Menu",command=analytics_data_window.destroy)
        back_to_menu_button.grid()

######################################Graph########################################################

        def analytics_graph():
            graph_window = tk.Toplevel(self)
            graph_window.geometry("800x600")
            graph_window.title("Graph")

            sns.set(style="darkgrid")
            plt.figure(figsize=(10, 8))
            sns.lineplot(graph_df, x="date", y="calculated_streak", hue="habit_name", marker='o')
            plt.xlabel('Date')
            plt.ylabel('Streak')
            plt.title('Habit Streak Over Time')
            plt.xticks(rotation=45)
            plt.legend(loc='upper right')
            plt.tight_layout()
            # Scale Axis
            plt.ylim(bottom=0)
            # Embed the Seaborn plot in the Tkinter application
            canvas = FigureCanvasTkAgg(plt.gcf(), master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack()

        if len(graph_df)>1:
            plot_button = tk.Button(analytics_data_window, text="Plot Graph", command=analytics_graph)
            plot_button.grid()