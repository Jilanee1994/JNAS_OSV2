class SessionManager:

    def __init__(self):
        self.logged_in = False

    def login(self):
        self.logged_in = True

    def logout(self):
        self.logged_in = False

    def status(self):
        return self.logged_in
