# nlp.py
import dateparser
from ui import console

def parse_command(command):
    try:
        command = command.lower().strip()
        if command.startswith("add task"):
            parts = command.split(" ", 2)[2].strip().split(" due ")
            title = parts[0].strip()
            due_date = dateparser.parse(parts[1]).strftime('%Y-%m-%d') if len(parts) > 1 else None
            return {"action": "add", "title": title, "due_date": due_date}
        elif command.startswith("complete task"):
            task_id = command.split(" ", 2)[2].strip()
            return {"action": "complete", "task_id": task_id}
        elif command.startswith("assign task"):
            parts = command.split(" to ", 1)
            task_id = parts[0].split(" ", 2)[2].strip()
            username = parts[1].strip()
            return {"action": "assign", "task_id": task_id, "username": username}
        elif command.startswith("filter by tag"):
            tag = command.split(" ", 3)[3].strip()
            return {"action": "filter", "tag": tag}
        elif command.startswith("sort by"):
            criteria = command.split(" ", 2)[2].strip()
            return {"action": "sort", "criteria": criteria}
        return {"action": "unknown"}
    except Exception as e:
        console.print(f"[red]Error parsing command: {e}[/red]")
        return {"action": "unknown"}