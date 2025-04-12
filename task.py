from enum import Enum
from datetime import datetime, timedelta
import uuid
from database import Database
import schedule
import time
from ui import console

class Priority(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Status(Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

class Recurrence(Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"

class Task:
    def __init__(self, title, description, priority, due_date=None, tags=None,
                 recurrence=None, parent_id=None, user_id=None, assigned_to=None,
                 id=None, status="To Do", created_at=None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = Priority(priority)
        self.status = Status(status)
        self.due_date = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None
        self.tags = tags if tags else []
        self.recurrence = Recurrence(recurrence) if recurrence else None
        self.parent_id = parent_id
        self.user_id = user_id
        self.assigned_to = assigned_to
        self.created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S') if created_at else datetime.now()
        self.db = Database()

    def save(self):
        task_data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'tags': self.tags,
            'recurrence': self.recurrence.value if self.recurrence else None,
            'parent_id': self.parent_id,
            'user_id': self.user_id,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.db.insert_task(task_data)
        self.setup_reminder()

    def update(self, **kwargs):
        updates = {}
        for key, value in kwargs.items():
            if key == 'title':
                self.title = value
                updates['title'] = value
            elif key == 'description':
                self.description = value
                updates['description'] = value
            elif key == 'priority':
                self.priority = Priority(value)
                updates['priority'] = self.priority.value
            elif key == 'status':
                self.status = Status(value)
                updates['status'] = self.status.value
            elif key == 'due_date':
                self.due_date = datetime.strptime(value, '%Y-%m-%d') if value else None
                updates['due_date'] = self.due_date.strftime('%Y-%m-%d') if self.due_date else None
            elif key == 'tags':
                self.tags = value if value else []
                updates['tags'] = self.tags
            elif key == 'assigned_to':
                self.assigned_to = value
                updates['assigned_to'] = value
        self.db.update_task(self.id, updates)

    def delete(self):
        self.db.delete_task(self.id)

    def setup_reminder(self):
        if self.due_date:
            def check_due():
                if self.due_date.date() == datetime.now().date():
                    console.print(f"[yellow]Reminder: Task '{self.title}' is due today![/yellow]")
            schedule.every().day.at("09:00").do(check_due)

    def generate_recurring(self):
        if not self.recurrence or not self.due_date:
            return
        if self.due_date < datetime.now():
            new_due_date = self.due_date
            if self.recurrence == Recurrence.DAILY:
                new_due_date += timedelta(days=1)
            elif self.recurrence == Recurrence.WEEKLY:
                new_due_date += timedelta(weeks=1)
            elif self.recurrence == Recurrence.MONTHLY:
                new_due_date += timedelta(days=30)
            new_task = Task(
                self.title, self.description, self.priority.value,
                new_due_date.strftime('%Y-%m-%d'), self.tags,
                self.recurrence.value, self.parent_id, self.user_id,
                self.assigned_to
            )
            new_task.save()

    @staticmethod
    def get_tasks(user_id):
        db = Database()
        tasks = db.find_tasks({'user_id': user_id})
        return [Task(**{k: v for k, v in task.items() if k != '_id'}) for task in tasks]

    @staticmethod
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)
