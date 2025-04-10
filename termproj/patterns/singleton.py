# patterns/singleton.py
"""
Singleton pattern to manage the current user session.
This ensures only one instance holds the logged-in user information.
"""
class UserSessionSingleton:
    __instance = None

    def __init__(self):
        if UserSessionSingleton.__instance is not None:
            raise Exception("This class is a singleton!")
        self.user_id = None
        self.email = None
        self.name = None 
        UserSessionSingleton.__instance = self

    @staticmethod
    def get_instance():
        if UserSessionSingleton.__instance is None:
            UserSessionSingleton()
        return UserSessionSingleton.__instance

    def login(self, user_id, email, name):
        self.user_id = user_id
        self.email = email
        self.name = name

    def logout(self):
        self.user_id = None
        self.email = None
        self.name = None

    def is_logged_in(self):
        return self.user_id is not None
