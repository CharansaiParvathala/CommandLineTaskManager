# user.py
from database import Database
from datetime import datetime, timedelta
import uuid
from ui import console

class User:
    def __init__(self, username, password, user_id=None, streak=0, last_completion=None):
        self.username = username
        self.password = password
        self.user_id = user_id or str(uuid.uuid4())
        self.streak = streak
        self.last_completion = last_completion
        self.db = Database()

    def save(self):
        user_data = {
            'id': self.user_id,
            'username': self.username,
            'password': self.password,
            'streak': self.streak,
            'last_completion': self.last_completion
        }
        self.db.insert_user(user_data)

    def complete_task(self, task):
        task.update(status="Done")
        today = datetime.now().date()
        if self.last_completion and self.last_completion == str(today - timedelta(days=1)):
            self.streak += 1
        else:
            self.streak = 1
        self.last_completion = str(today)
        self.db.update_user(self.user_id, {'streak': self.streak, 'last_completion': self.last_completion})
        console.print(f"[green]Streak: {self.streak} days![/green]")

    @staticmethod
    def login(username, password):
        db = Database()
        user = db.find_user({'username': username, 'password': password})
        if user:
            return User(user['username'], user['password'], user['id'], user.get('streak', 0), user.get('last_completion'))
        return None