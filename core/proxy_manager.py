class ProxyManager:

    def __init__(self, server=None):
        self.server = server

    def get_proxy(self):
        return self.server
