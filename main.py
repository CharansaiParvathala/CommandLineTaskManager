from task import Task
from user import User
from cli import render_task_tree
from pomodoro import start_pomodoro
from nlp import parse_command
from charts import plot_task_distribution, plot_priority_bar, plot_gantt_chart
from utils import export_to_csv
from database import Database
from ui import console
from rich.progress import Progress, SpinnerColumn, TextColumn
import threading, os, time
import sys

SESSION_FILE = "session.txt"
db = Database()

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            username, password = f.read().strip().split('\n')
            return username, password
    return None, None

def save_session(username, password):
    with open(SESSION_FILE, "w") as f:
        f.write(f"{username}\n{password}")

def delete_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def loading_task(message, func, *args, **kwargs):
    result = None
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task(f"{message}...", total=None)
        thread = threading.Thread(target=lambda: func(*args, **kwargs), daemon=True)
        thread.start()
        while thread.is_alive():
            time.sleep(0.1)
        progress.remove_task(task)
        result = func(*args, **kwargs)
    return result

def main():
    # Initial startup loading
    with Progress(SpinnerColumn(), TextColumn("[bold green]Starting CLI Task Manager...")) as progress:
        progress.add_task("Loading...", total=None)
        time.sleep(1.2)

    user = None
    username, password = load_session()
    if username and password:
        console.print(f"[cyan]Attempting auto-login for {username}...[/cyan]")
        user = loading_task("Logging in", User.login, username, password)
        if user:
            console.print(f"[green]Auto-logged in as {username}[/green]")

    if not user:
        while not user:
            action = input("Register or Login (r/l): ").lower()
            username = input("Username: ")
            password = input("Password: ")
            if action == 'r':
                user = User(username, password)
                loading_task("Registering user", user.save)
                console.print(f"[green]User '{username}' registered![/green]")
            elif action == 'l':
                user = loading_task("Logging in", User.login, username, password)
                if not user:
                    console.print("[red]Invalid credentials.[/red]")
            else:
                console.print("[red]Invalid command.[/red]")
        save_session(username, password)

    threading.Thread(target=Task.run_scheduler, daemon=True).start()

    while True:
        console.print("\n[bold yellow]Commands:[/bold yellow] add, view, updt, del, cmplt, pdr, charts, assign, filt, sort, exp, logout, quit")
        command = input("Command: ").lower()

        if command == "add":
            title = input("Title: ")
            description = input("Description: ")
            priority = input("Priority (Low/Medium/High): ")
            due_date = input("Due Date (YYYY-MM-DD, optional): ") or None
            tags = input("Tags (comma-separated, optional): ").split(',') if input("Add tags? (y/n): ") == 'y' else []
            recurrence = input("Recurrence (Daily/Weekly/Monthly, optional): ") or None
            parent_id = input("Parent Task ID (optional): ") or None
            task = Task(title, description, priority, due_date, tags, recurrence, parent_id, user.user_id)
            loading_task("Saving task", task.save)
            console.print("[green]Task added![/green]")


        elif command == "view":

            tasks = Task.get_tasks(user.user_id)

            for task in tasks:
                task.generate_recurring()

            tasks = Task.get_tasks(user.user_id)

            console.print("\n[bold green]Task List[/bold green]:")

            for task in tasks:
                console.print(
                    f"[bold]{task.id}[/bold] - {task.title} (Priority: {task.priority}, Status: {task.status})")

            render_task_tree(tasks)

        elif command == "updt":
            task_id = input("Task ID: ")
            task_data = db.find_tasks({'id': task_id, 'user_id': user.user_id})
            if task_data:
                task = task_data[0]
                if '_id' in task:
                    task['id'] = task.pop('_id')
                task = Task(**task)
                console.print("[yellow](Leave blank to keep current value)[/yellow]")
                title = input("Title: ") or task.title
                description = input("Description: ") or task.description
                priority = input("Priority: ") or task.priority.value
                status = input("Status: ") or task.status.value
                due_date = input("Due Date: ") or (task.due_date.strftime('%Y-%m-%d') if task.due_date else None)
                tags = input("Tags (comma-separated): ")
                loading_task("Updating task", task.update,
                             title=title, description=description, priority=priority, status=status,
                             due_date=due_date, tags=tags.split(',') if tags else task.tags)
                console.print("[green]Task updated![/green]")
            else:
                console.print("[red]Task not found.[/red]")


        elif command == "del":
            task_id = input("Task ID: ")
            task_data = db.find_tasks({'id': task_id, 'user_id': user.user_id})
            if task_data:
                task = task_data[0]
                if '_id' in task:
                    task['id'] = task.pop('_id')
                task = Task(**task)
                if input(f"Confirm delete '{task.title}'? (y/n): ").lower() == 'y':
                    loading_task("Deleting task", task.delete)
                    console.print("[green]Task deleted![/green]")
                else:
                    console.print("[yellow]Deletion cancelled.[/yellow]")
            else:
                console.print("[red]Task not found.[/red]")

        elif command == "cmplt":
            task_id = input("Task ID: ")
            task_data = db.find_tasks({'id': task_id, 'user_id': user.user_id})
            if task_data:
                task = task_data[0]
                if '_id' in task:
                    task['id'] = task.pop('_id')
                task = Task(**task)
                loading_task("Completing task", user.complete_task, task)
                console.print("[green]Task completed![/green]")
            else:
                console.print("[red]Task not found.[/red]")

        elif command == "pdr":
            start_pomodoro()

        elif command == "charts":
            tasks = Task.get_tasks(user.user_id)
            loading_task("Generating charts", plot_task_distribution, tasks)
            plot_priority_bar(tasks)
            plot_gantt_chart(tasks)

        elif command == "assign":
            task_id = input("Task ID: ")
            username = input("Assign to username: ")
            task_data = db.find_tasks({'id': task_id, 'user_id': user.user_id})
            if task_data:
                task = task_data[0]
                if '_id' in task:
                    task['id'] = task.pop('_id')
                task = Task(**task)
                if db.find_user({'username': username}):
                    loading_task("Assigning task", task.update, assigned_to=username)
                    console.print(f"[green]Task assigned to '{username}'.[/green]")
                else:
                    console.print("[red]User not found.[/red]")
            else:
                console.print("[red]Task not found.[/red]")

        elif command == "filt":
            tag = input("Tag: ")
            tasks = [t for t in Task.get_tasks(user.user_id) if tag in t.tags]
            render_task_tree(tasks)

        elif command == "sort":
            criteria = input("Sort by (priority/due_date): ")
            tasks = Task.get_tasks(user.user_id)
            if criteria == "priority":
                tasks.sort(key=lambda x: ['High', 'Medium', 'Low'].index(x.priority.value))
            elif criteria == "due_date":
                tasks.sort(key=lambda x: x.due_date.isoformat() if x.due_date else '9999-12-31')
            render_task_tree(tasks)

        elif command == "exp":
            filename = input("Export filename (e.g., tasks.csv): ")
            tasks = Task.get_tasks(user.user_id)
            loading_task("Exporting tasks", export_to_csv, tasks, filename)
            console.print(f"[green]Tasks exported to '{filename}'[/green]")

        elif command == "logout":
            delete_session()
            console.print("[yellow]Logged out successfully.[/yellow]")
            os.execv(sys.executable, ['python'] + sys.argv)

        elif command == "quit":
            break

        else:
            parsed = parse_command(command)
            console.print("[red]Unknown command.[/red]")

if __name__ == "__main__":
    main()
