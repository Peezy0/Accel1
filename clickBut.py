import tkinter as tk
import sqlite3

# Establish a connection to the SQLite database
conn = sqlite3.connect('projectbase.db')
c = conn.cursor()

# Drop existing table if it exists (for schema updates, if necessary)
c.execute('''DROP TABLE IF EXISTS proficiencies''')

# Create a new table for goals
c.execute('''CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_text TEXT)''')

# Create a new table for proficiencies linked to goals
c.execute('''CREATE TABLE IF NOT EXISTS proficiencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proficiency_text TEXT,
                goal_id INTEGER,
                assessment_area_id INTEGER,
                slo_id INTEGER,
                FOREIGN KEY(goal_id) REFERENCES goals(id),
                FOREIGN KEY(assessment_area_id) REFERENCES assessment_areas(id),
                FOREIGN KEY(slo_id) REFERENCES slo_table(id))''')

# Create a new table for SLOs linked to goals
c.execute('''CREATE TABLE IF NOT EXISTS slo_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slo_text TEXT,
                goal_id INTEGER,
                FOREIGN KEY(goal_id) REFERENCES goals(id))''')

# Create a new table for assessment areas linked to goals
c.execute('''CREATE TABLE IF NOT EXISTS assessment_areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area_name TEXT,
                goal_id INTEGER,
                FOREIGN KEY(goal_id) REFERENCES goals(id))''')

# Create a new table for courses linked to goals and proficiencies
c.execute('''CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT,
                goal_id INTEGER,
                proficiency_id INTEGER,
                FOREIGN KEY(goal_id) REFERENCES goals(id),
                FOREIGN KEY(proficiency_id) REFERENCES proficiencies(id))''')

conn.commit()

goal_var = None
goal_menu = None
program_name = ""

class GoalWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Goal Window")
        self.geometry("800x600")
        self.entry_label = tk.Label(self, text="Enter your goal:")
        self.entry_label.pack()
        self.entry = tk.Entry(self)
        self.entry.pack()
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_data)
        self.submit_button.pack()
        self.display_label = tk.Label(self, text="")
        self.display_label.pack()

    def submit_data(self):
        goal_text = self.entry.get()
        print("Entered Goal:", goal_text)
        # Insert a new goal into the 'goals' table
        c.execute("INSERT INTO goals (goal_text) VALUES (?)", (goal_text,))
        conn.commit()
        self.display_label.config(text=f"Goal: {goal_text}")
        self.entry.delete(0, tk.END)
        refresh_goal_list()

class ProficiencyWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Proficiencies Window")
        self.geometry("800x600")
        self.goal_label = tk.Label(self, text="Select Goal:")
        self.goal_label.pack()
        self.goal_var = tk.StringVar()
        self.goal_var.trace("w", self.update_dropdowns)  # Update assessment areas and SLOs on goal change
        self.goal_menu = tk.OptionMenu(self, self.goal_var, *get_goals())
        self.goal_menu.pack()
        self.assessment_area_label = tk.Label(self, text="Select Assessment Area:")
        self.assessment_area_label.pack()
        self.assessment_area_var = tk.StringVar()
        self.assessment_area_menu = tk.OptionMenu(self, self.assessment_area_var, "")
        self.assessment_area_menu.pack()
        self.slo_label = tk.Label(self, text="Select SLO:")
        self.slo_label.pack()
        self.slo_var = tk.StringVar()
        self.slo_menu = tk.OptionMenu(self, self.slo_var, "")
        self.slo_menu.pack()
        self.entry_label = tk.Label(self, text="Enter Proficiencies (separated by commas):")
        self.entry_label.pack()
        self.entry = tk.Entry(self)
        self.entry.pack()
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_data)
        self.submit_button.pack()
        self.display_label = tk.Label(self, text="")
        self.display_label.pack()

    def update_dropdowns(self, *args):
        goal_id = self.goal_var.get().split(":")[0]
        assessment_areas = get_assessment_areas_for_goal(goal_id)
        slos = get_slos_for_goal(goal_id)

        # Update assessment area dropdown
        menu = self.assessment_area_menu["menu"]
        menu.delete(0, "end")
        for area in assessment_areas:
            menu.add_command(label=area, command=lambda value=area: self.assessment_area_var.set(value))

        # Update SLO dropdown
        menu = self.slo_menu["menu"]
        menu.delete(0, "end")
        for slo in slos:
            menu.add_command(label=slo, command=lambda value=slo: self.slo_var.set(value))

    def submit_data(self):
        proficiency_text = self.entry.get()
        goal_id = self.goal_var.get().split(":")[0]
        assessment_area_id = self.assessment_area_var.get().split(":")[0]
        slo_id = self.slo_var.get().split(":")[0]
        prof_list = proficiency_text.split(',')
        print("Entered Proficiencies:", proficiency_text)
        print("Selected Goal ID:", goal_id)
        print("Selected Assessment Area ID:", assessment_area_id)
        print("Selected SLO ID:", slo_id)
        # Insert the proficiencies into the 'proficiencies' table with the corresponding goal ID, assessment area ID, and SLO ID
        for proficiency in prof_list:
            c.execute("INSERT INTO proficiencies (proficiency_text, goal_id, assessment_area_id, slo_id) VALUES (?, ?, ?, ?)", 
                      (proficiency.strip(), goal_id, assessment_area_id, slo_id))
        conn.commit()
        self.display_label.config(text=f"Proficiencies: {proficiency_text}")
        self.entry.delete(0, tk.END)

class InputSLOWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Input SLO Window")
        self.geometry("800x600")
        self.goal_label = tk.Label(self, text="Select Goal:")
        self.goal_label.pack()
        self.goal_var = tk.StringVar()
        self.goal_menu = tk.OptionMenu(self, self.goal_var, *get_goals())
        self.goal_menu.pack()
        self.entry_label = tk.Label(self, text="Enter Student Learning Outcomes (separated by commas):")
        self.entry_label.pack()
        self.entry = tk.Entry(self)
        self.entry.pack()
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_data)
        self.submit_button.pack()
        self.display_label = tk.Label(self, text="")
        self.display_label.pack()

    def submit_data(self):
        slo_text = self.entry.get()
        goal_id = self.goal_var.get().split(":")[0]
        slo_list = slo_text.split(',')
        print("Entered Student Learning Outcomes:", slo_text)
        print("Selected Goal ID:", goal_id)
        # Insert the SLOs into the 'slo_table' with the corresponding goal ID
        for slo in slo_list:
            c.execute("INSERT INTO slo_table (slo_text, goal_id) VALUES (?, ?)", (slo.strip(), goal_id))
        conn.commit()
        self.display_label.config(text=f"Student Learning Outcomes: {slo_text}")
        self.entry.delete(0, tk.END)

class AssessmentAreaWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Assessment Area Window")
        self.geometry("800x600")
        self.goal_label = tk.Label(self, text="Select Goal:")
        self.goal_label.pack()
        self.goal_var = tk.StringVar()
        self.goal_menu = tk.OptionMenu(self, self.goal_var, *get_goals())
        self.goal_menu.pack()
        self.entry_label = tk.Label(self, text="Enter Assessment Area Name:")
        self.entry_label.pack()
        self.entry = tk.Entry(self)
        self.entry.pack()
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_data)
        self.submit_button.pack()
        self.display_label = tk.Label(self, text="")
        self.display_label.pack()

    def submit_data(self):
        area_name = self.entry.get()
        goal_id = self.goal_var.get().split(":")[0]
        print("Entered Assessment Area Name:", area_name)
        print("Selected Goal ID:", goal_id)
        # Insert a new assessment area into the 'assessment_areas' table with the corresponding goal ID
        c.execute("INSERT INTO assessment_areas (area_name, goal_id) VALUES (?, ?)", (area_name, goal_id))
        conn.commit()
        self.display_label.config(text=f"Assessment Area Name: {area_name}")
        self.entry.delete(0, tk.END)

class CourseWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Course Window")
        self.geometry("800x600")
        self.goal_label = tk.Label(self, text="Select Goal:")
        self.goal_label.pack()
        self.goal_var = tk.StringVar()
        self.goal_var.trace("w", self.update_proficiency_menu)  # Update proficiency list on goal change
        self.goal_menu = tk.OptionMenu(self, self.goal_var, *get_goals())
        self.goal_menu.pack()
        self.proficiency_label = tk.Label(self, text="Select Proficiency:")
        self.proficiency_label.pack()
        self.proficiency_var = tk.StringVar()
        self.proficiency_menu = tk.OptionMenu(self, self.proficiency_var, "")
        self.proficiency_menu.pack()
        self.entry_label = tk.Label(self, text="Enter Course Name:")
        self.entry_label.pack()
        self.entry = tk.Entry(self)
        self.entry.pack()
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_data)
        self.submit_button.pack()
        self.display_label = tk.Label(self, text="")
        self.display_label.pack()

    def update_proficiency_menu(self, *args):
        goal_id = self.goal_var.get().split(":")[0]
        proficiencies = get_proficiencies_for_goal(goal_id)
        menu = self.proficiency_menu["menu"]
        menu.delete(0, "end")
        for proficiency in proficiencies:
            menu.add_command(label=proficiency, command=lambda value=proficiency: self.proficiency_var.set(value))

    def submit_data(self):
        course_name = self.entry.get()
        goal_id = self.goal_var.get().split(":")[0]
        proficiency_id = self.proficiency_var.get().split(":")[0]
        print("Entered Course Name:", course_name)
        print("Selected Goal ID:", goal_id)
        print("Selected Proficiency ID:", proficiency_id)
        # Insert a new course into the 'courses' table with the corresponding goal ID and proficiency ID
        c.execute("INSERT INTO courses (course_name, goal_id, proficiency_id) VALUES (?, ?, ?)", 
                  (course_name, goal_id, proficiency_id))
        conn.commit()
        self.display_label.config(text=f"Course Name: {course_name}")
        self.entry.delete(0, tk.END)

class OpenPastWorkWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("Past Work")
        self.load_past_work()

    def load_past_work(self):
        c.execute("SELECT * FROM goals ORDER BY id DESC LIMIT 1")
        goal = c.fetchone()
        if goal:
            goal_id = goal[0]
            data = {
                "Goal": goal[1],
                "Proficiencies": ', '.join(get_proficiencies_for_goal(goal_id)),
                "SLOs": ', '.join(get_slos_for_goal(goal_id)),
                "Assessment Areas": ', '.join(get_assessment_areas_for_goal(goal_id)),
                "Courses": ', '.join(get_courses_for_goal(goal_id))
            }
            for key, value in data.items():
                label = tk.Label(self, text=f"{key}: {value}")
                label.pack()
        else:
            label = tk.Label(self, text="No past work found.")
            label.pack()

def get_goals():
    c.execute("SELECT id, goal_text FROM goals")
    goals = c.fetchall()
    return [f"{goal[0]}: {goal[1]}" for goal in goals]

def get_proficiencies_for_goal(goal_id):
    c.execute("SELECT id, proficiency_text FROM proficiencies WHERE goal_id = ?", (goal_id,))
    proficiencies = c.fetchall()
    return [f"{proficiency[0]}: {proficiency[1]}" for proficiency in proficiencies]

def get_slos_for_goal(goal_id):
    c.execute("SELECT slo_text FROM slo_table WHERE goal_id = ?", (goal_id,))
    slos = c.fetchall()
    return [slo[0] for slo in slos]

def get_assessment_areas_for_goal(goal_id):
    c.execute("SELECT id, area_name FROM assessment_areas WHERE goal_id = ?", (goal_id,))
    areas = c.fetchall()
    return [f"{area[0]}: {area[1]}" for area in areas]

def get_courses_for_goal(goal_id):
    c.execute("SELECT course_name FROM courses WHERE goal_id = ?", (goal_id,))
    courses = c.fetchall()
    return [course[0] for course in courses]

def refresh_goal_list():
    global goal_menu, goal_var
    if goal_menu is not None and goal_var is not None:
        goals = get_goals()
        menu = goal_menu["menu"]
        menu.delete(0, "end")
        for goal in goals:
            menu.add_command(label=goal, command=lambda value=goal: goal_var.set(value))

def open_goal():
    GoalWindow()

def open_proficiency():
    ProficiencyWindow()

def open_input_slo():
    InputSLOWindow()

def open_assessment_area():
    AssessmentAreaWindow()

def open_course():
    CourseWindow()

def close_window():
    root.destroy()

def open_past_work():
    OpenPastWorkWindow()

def open_new_work():
    print("New work button clicked.")
    create_new_row()
    show_welcome_page()

def create_new_row():
    c.execute("INSERT INTO goals (goal_text) VALUES (NULL)")
    conn.commit()

def show_welcome_page():
    menu_frame.pack_forget()
    welcome_frame.pack()

def submit_program_name():
    global program_name
    program_name = program_name_entry.get()
    welcome_frame.pack_forget()
    show_menu_page()

def show_menu_page():
    global goal_var, goal_menu
    new_page_label.config(text=f"Welcome {program_name}, choose an option")
    new_page_frame.pack()
    refresh_goal_list()
    goals = get_goals()
    goal_var = tk.StringVar()
    goal_menu = tk.OptionMenu(new_page_frame, goal_var, *goals)
    goal_menu.pack()

def go_back():
    new_page_frame.pack_forget()
    menu_frame.pack()

root = tk.Tk()
root.geometry("900x900")

menu_frame = tk.Frame(root)

menu_label = tk.Label(menu_frame, text="Menu", font=('Arial', 20))
menu_label.pack(pady=20)

new_work_button = tk.Button(menu_frame, text="New Work", command=open_new_work)
new_work_button.pack(pady=10)

open_work_button = tk.Button(menu_frame, text="Open Past Work", command=open_past_work)
open_work_button.pack(pady=10)

close_button = tk.Button(menu_frame, text="Close", command=close_window)
close_button.pack(pady=10)

menu_frame.pack()

welcome_frame = tk.Frame(root)

welcome_label = tk.Label(welcome_frame, text="Welcome: Enter your program name", font=("Arial", 18))
welcome_label.pack(pady=20)

program_name_entry = tk.Entry(welcome_frame)
program_name_entry.pack(pady=10)

submit_name_button = tk.Button(welcome_frame, text="Submit", command=submit_program_name)
submit_name_button.pack(pady=10)

new_page_frame = tk.Frame(root)

new_page_label = tk.Label(new_page_frame, text="Choose an option", font=("Arial", 18))
new_page_label.pack(pady=10)

goal_button = tk.Button(new_page_frame, text="Goals", command=open_goal)
goal_button.pack(pady=10)

slo_button = tk.Button(new_page_frame, text="Student Learning Outcomes", command=open_input_slo)
slo_button.pack(pady=10)


area_button = tk.Button(new_page_frame, text="Assessment Area", command=open_assessment_area)
area_button.pack(pady=10)


proficiency_button = tk.Button(new_page_frame, text="Proficiencies", command=open_proficiency)
proficiency_button.pack(pady=10)

course_button = tk.Button(new_page_frame, text="Courses", command=open_course)
course_button.pack(pady=10)

back_button = tk.Button(new_page_frame, text="Back", command=go_back)
back_button.pack(pady=10)

new_page_frame.pack_forget()

root.mainloop()
