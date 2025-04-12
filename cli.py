from rich.tree import Tree
from rich.text import Text
from config import THEME
from ui import console

def render_task_tree(tasks, parent_id=None, tree=None):
    if tree is None:
        tree = Tree("Tasks", style=THEME)

    for task in tasks:
        if task.parent_id == parent_id:
            branch = tree.add(Text(task.title, style="bold magenta"))

            # Fix: Use `.value` to convert Enum to string
            priority_str = task.priority.value if hasattr(task.priority, 'value') else task.priority
            status_str = task.status.value if hasattr(task.status, 'value') else task.status

            priority_color = {"Low": "green", "Medium": "yellow", "High": "red"}.get(priority_str, "white")
            status_color = {"To Do": "blue", "In Progress": "cyan", "Done": "green"}.get(status_str, "white")

            details = f"Priority: {priority_str} | Status: {status_str} | Due: {task.due_date or 'None'}"
            branch.add(Text(details, style=priority_color))

            if task.tags:
                branch.add(Text(f"Tags: {', '.join(task.tags)}", style="dim"))

            # Fix: `task` is an object, not a dict
            if hasattr(task, 'assigned_to') and task.assigned_to:
                branch.add(Text(f"Assigned to: {task.assigned_to}", style="cyan"))

            # Recursively render children
            render_task_tree(tasks, task.id, branch)

    if parent_id is None:
        console.print(tree)
