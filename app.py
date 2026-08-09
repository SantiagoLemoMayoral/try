from datetime import date

class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self.state = None

    def __repr__(self):
        return{
            f'id: {self.id} | name: {self.name}| email : {self.email}| state: {self.state}'
        } 


class Project:
    def __init__(self, id, name, description, owner):
        self.id = id
        self.name = name
        self.description = description
        self.owner = owner
        self.members = []
        self.creation_date = date.today()

class Task:
    def __init__(self, id, title, description, priority, status, project_ID, assigned_user_ID, created_date, deadline):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.project_ID = project_ID
        self.assigned_user_ID = assigned_user_ID
        self.created_date = created_date
        self.deadline = deadline

class App:
    def __init__(self):
        self.users = {}
        self.projects = {}
        self.tasks = {}

    def find_user(self, user_id):
        for u in self.users:
            if u.id == user_id:
                return u
        return None

    def find_project(self, project_id):
        for p in self.projects:
            if p.id == project_id:
                return p
        return None

    def find_task(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None
    
    def create_user(self, user_id):
        user = self.find_user(user_id)

        if user is not None:
            print(f'USER ALREADY IN')
            return None

        self.users.add(user)
        




    

