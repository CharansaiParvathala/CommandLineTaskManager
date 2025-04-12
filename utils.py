# utils.py
from datetime import datetime
import csv
from ui import console

def format_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        except ValueError:
            return date_str
    return "None"

def export_to_csv(tasks, filename):
    if not tasks:
        console.print("[yellow]No tasks to export.[/yellow]")
        return
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Title', 'Description', 'Priority', 'Status', 'Due Date', 'Tags', 'Assigned To'])
        for task in tasks:
            writer.writerow([
                task['id'],
                task['title'],
                task['description'],
                task['priority'],
                task['status'],
                task['due_date'],
                ", ".join(task['tags']),
                task.get('assigned_to', '')
            ])
    console.print(f"[green]Tasks exported to {filename}.[/green]")