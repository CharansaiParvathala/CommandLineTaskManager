# database.py
from pymongo import MongoClient
from config import MONGODB_URL

class Database:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        # Extract database name from URI or specify it explicitly
        # If your URI includes the database (e.g., /task_manager), this works
        # If not, replace 'task_manager' with your desired database name
        self.db = self.client.get_database('task_manager')  # Explicitly specify database name

    def insert_task(self, task_data):
        tasks_collection = self.db['tasks']
        return tasks_collection.insert_one(task_data).inserted_id

    def find_tasks(self, query):
        tasks_collection = self.db['tasks']
        return list(tasks_collection.find(query))

    def update_task(self, task_id, updates):
        tasks_collection = self.db['tasks']
        tasks_collection.update_one({'id': task_id}, {'$set': updates})

    def delete_task(self, task_id):
        tasks_collection = self.db['tasks']
        tasks_collection.delete_one({'id': task_id})

    def insert_user(self, user_data):
        users_collection = self.db['users']
        return users_collection.insert_one(user_data).inserted_id

    def find_user(self, query):
        users_collection = self.db['users']
        return users_collection.find_one(query)

    def update_user(self, user_id, updates):
        users_collection = self.db['users']
        users_collection.update_one({'id': user_id}, {'$set': updates})