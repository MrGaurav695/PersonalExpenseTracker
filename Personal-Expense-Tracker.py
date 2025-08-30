import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import csv
from tabulate import tabulate

# Initialize database and table
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL
        )
    ''')
    conn.commit()
    conn.close()

# Add an expense record
def add_expense(date, category, amount):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)', (date, category, amount))
    conn.commit()
    conn.close()

# Get total spending and spending by category
def get_spending_summary(month=None):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    if month:
        c.execute("SELECT SUM(amount) FROM expenses WHERE strftime('%Y-%m', date)=?", (month,))
        total = c.fetchone()[0] or 0
        c.execute("SELECT category, SUM(amount) FROM expenses WHERE strftime('%Y-%m', date)=? GROUP BY category", (month,))
        category_data = c.fetchall()
    else:
        c.execute('SELECT SUM(amount) FROM expenses')
        total = c.fetchone()[0] or 0
        c.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
        category_data = c.fetchall()

    conn.close()
    return total, category_data

# Plot pie chart of spending by category and save as image
def plot_pie_chart(category_data, filename='spending_chart.png'):
    categories = [row[0] for row in category_data]
    amounts = [row[1] for row in category_data]

    if not categories:
        print("No data to plot.")
        return

    plt.figure(figsize=(7,7))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Spending by Category')
    plt.savefig(filename)
    plt.show()
    print(f"Pie chart saved as {filename}")

# Export data to CSV
def export_to_csv():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('SELECT date, category, amount FROM expenses ORDER BY date')
    data = c.fetchall()
    conn.close()

    with open('expenses.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Category', 'Amount'])
        writer.writerows(data)

    print("Data exported to expenses.csv")

# Display expenses in a table
def display_table():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('SELECT date, category, amount FROM expenses ORDER BY date')
    data = c.fetchall()
    conn.close()

    if data:
        print(tabulate(data, headers=['Date', 'Category', 'Amount'], tablefmt='grid'))
    else:
        print("No expenses recorded yet.")

def main():
    init_db()
    print("Welcome to Personal Expense Tracker")

    while True:
        print("\nOptions:")
        print("1. Add expense")
        print("2. Show total spending and pie chart")
        print("3. Show monthly spending summary")
        print("4. Export expenses to CSV")
        print("5. Show all expenses table")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            date = input("Enter date (YYYY-MM-DD) or leave blank for today: ")
            if not date:
                date = datetime.today().strftime('%Y-%m-%d')

            category = input("Enter category: ").strip().lower()
            try:
                amount = float(input("Enter amount: "))
            except ValueError:
                print("Invalid amount. Please enter a number.")
                continue
            add_expense(date, category, amount)
            print("Expense added.")

        elif choice == '2':
            total, category_data = get_spending_summary()
            print(f"\nTotal spending: ₹{total:.2f}")
            if category_data:
                plot_pie_chart(category_data)
            else:
                print("No expenses recorded yet.")

        elif choice == '3':
            month = input("Enter month in YYYY-MM format (e.g., 2025-08): ")
            total, category_data = get_spending_summary(month)
            print(f"\nTotal spending for {month}: ₹{total:.2f}")
            if category_data:
                plot_pie_chart(category_data, filename=f'spending_{month}.png')
            else:
                print("No expenses recorded for this month.")

        elif choice == '4':
            export_to_csv()

        elif choice == '5':
            display_table()

        elif choice == '6':
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == '__main__':
    main()
