# patterns/mediator.py
"""
Mediator pattern allows different UI components to communicate
without being directly coupled. Components send messages via the mediator.
"""
class UIMediator:
    def __init__(self):
        self._components = {}

    def register(self, name, component):
        self._components[name] = component
        component.mediator = self

    def send(self, message, sender_name):
        msg_type = message.get("type")
        if msg_type == "LOGIN_SUCCESS":
            if "main_window" in self._components:
                self._components["main_window"].on_user_logged_in(message["user_id"])
        elif msg_type == "SHOW_REGISTER":
            if "register_window" in self._components:
                self._components["register_window"].clear_fields()
                self._components["register_window"].show()
        elif msg_type == "SHOW_LOGIN":
            if "login_window" in self._components:
                self._components["login_window"].show()
        elif msg_type == "OPEN_PASSWORD_RECOVERY":
            if "password_recovery" in self._components:
                self._components["password_recovery"].show()
        # Additional message types can be added here.
