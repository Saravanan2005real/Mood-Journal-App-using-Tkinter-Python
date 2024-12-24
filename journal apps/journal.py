import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
import sqlite3
import datetime

# Database setup
def initialize_database():
    conn = sqlite3.connect("mood_journal.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Moods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            mood TEXT NOT NULL,
            journal_entry TEXT
        )
    """)
    conn.commit()
    conn.close()

# Insert entry into database
def add_mood_entry(date, mood, journal):
    try:
        conn = sqlite3.connect("mood_journal.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Moods (date, mood, journal_entry) VALUES (?, ?, ?)", (date, mood, journal))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Retrieve all entries from database
def fetch_all_entries():
    conn = sqlite3.connect("mood_journal.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Moods ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Fetch entry by date
def fetch_entry_by_date(date):
    conn = sqlite3.connect("mood_journal.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Moods WHERE date = ?", (date,))
    row = cursor.fetchone()
    conn.close()
    return row

# Tkinter GUI
class MoodJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mood Journal App")
        self.root.geometry("700x550")
        self.root.config(bg="#F0F8FF")

        # Header
        header = tk.Label(
            self.root,
            text="Mood Journal App",
            font=("Arial", 24, "bold"),
            fg="#4B0082",
            bg="#F0F8FF"
        )
        header.pack(pady=10)

        # Mood Selection
        mood_frame = tk.Frame(self.root, bg="#F0F8FF")
        mood_frame.pack(pady=10)

        tk.Label(mood_frame, text="Select Your Mood:", font=("Arial", 12), bg="#F0F8FF").pack(side=tk.LEFT, padx=5)
        self.mood_var = tk.StringVar(value="😊")
        mood_options = ["😊", "😔", "😡", "😌", "😎", "😭", "😴"]
        self.mood_menu = ttk.Combobox(mood_frame, values=mood_options, textvariable=self.mood_var, state="readonly", width=5)
        self.mood_menu.pack(side=tk.LEFT, padx=5)

        # Calendar for selecting date
        tk.Label(self.root, text="Select Date:", font=("Arial", 12), bg="#F0F8FF").pack(pady=5)
        self.calendar = Calendar(self.root, selectmode="day", date_pattern="yyyy-mm-dd")
        self.calendar.pack(pady=5)

        # Journal Entry
        tk.Label(self.root, text="Journal Entry:", font=("Arial", 12), bg="#F0F8FF").pack(pady=5)
        self.journal_entry = tk.Text(self.root, height=5, width=60, font=("Arial", 10))
        self.journal_entry.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#F0F8FF")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Save Entry", command=self.save_entry, bg="#810081", fg="white", font=("Arial", 10), width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="View History", command=self.view_history, bg="#4B0082", fg="white", font=("Arial", 10), width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Analyze Trends", command=self.analyze_trends, bg="#006400", fg="white", font=("Arial", 10), width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Search by Date", command=self.search_by_date, bg="#FFA500", fg="white", font=("Arial", 10), width=15).pack(side=tk.LEFT, padx=10)

    def save_entry(self):
        date = self.calendar.get_date()
        mood = self.mood_var.get()
        journal = self.journal_entry.get("1.0", tk.END).strip()
        if not mood or not journal:
            messagebox.showerror("Error", "Please select a mood and write a journal entry!")
            return

        if add_mood_entry(date, mood, journal):
            messagebox.showinfo("Success", "Mood entry saved successfully!")
            self.journal_entry.delete("1.0", tk.END)
        else:
            messagebox.showerror("Error", "You have already saved an entry for this date!")

    def view_history(self):
        entries = fetch_all_entries()
        if not entries:
            messagebox.showinfo("No Entries", "No mood entries found!")
            return

        history_window = tk.Toplevel(self.root)
        history_window.title("Mood History")
        history_window.geometry("500x400")
        history_window.config(bg="#F0F8FF")

        tk.Label(history_window, text="Mood History", font=("Arial", 16, "bold"), bg="#F0F8FF", fg="#4B0082").pack(pady=10)

        history_text = tk.Text(history_window, height=20, width=60, font=("Arial", 10))
        history_text.pack(pady=10)

        for entry in entries:
            date, mood, journal = entry[1], entry[2], entry[3]
            history_text.insert(tk.END, f"Date: {date}\nMood: {mood}\nEntry: {journal}\n{'-'*40}\n")
        history_text.config(state="disabled")

    def analyze_trends(self):
        entries = fetch_all_entries()
        if not entries:
            messagebox.showinfo("No Data", "No mood entries found for analysis!")
            return

        mood_counts = {}
        for entry in entries:
            mood = entry[2]
            mood_counts[mood] = mood_counts.get(mood, 0) + 1

        trends_window = tk.Toplevel(self.root)
        trends_window.title("Mood Trends")
        trends_window.geometry("300x300")
        trends_window.config(bg="#F0F8FF")

        tk.Label(trends_window, text="Mood Trends", font=("Arial", 16, "bold"), bg="#F0F8FF", fg="#4B0082").pack(pady=10)

        trends_text = tk.Text(trends_window, height=15, width=30, font=("Arial", 10))
        trends_text.pack(pady=10)

        for mood, count in mood_counts.items():
            trends_text.insert(tk.END, f"{mood}: {count} times\n")
        trends_text.config(state="disabled")

    def search_by_date(self):
        date = self.calendar.get_date()
        entry = fetch_entry_by_date(date)
        if not entry:
            messagebox.showinfo("No Entry", f"No mood entry found for {date}!")
            return

        search_window = tk.Toplevel(self.root)
        search_window.title("Search Result")
        search_window.geometry("400x300")
        search_window.config(bg="#F0F8FF")

        tk.Label(search_window, text=f"Entry for {date}", font=("Arial", 16, "bold"), bg="#F0F8FF", fg="#4B0082").pack(pady=10)

        result_text = tk.Text(search_window, height=10, width=50, font=("Arial", 10))
        result_text.pack(pady=10)

        mood, journal = entry[2], entry[3]
        result_text.insert(tk.END, f"Mood: {mood}\n\nJournal Entry:\n{journal}")
        result_text.config(state="disabled")

# Main Program
if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app = MoodJournalApp(root)
    root.mainloop()
