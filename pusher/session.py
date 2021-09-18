from .pusher import pusher

from config.settings import settings 
import pusher

class session():
    def __init__(self) -> None:
        """
            Pusher client session
        """
        self.pusher_client = pusher.Pusher(
            app_id = settings.pusher['app_id'],
            key = settings.pusher['key'],
            secret = settings.pusher['secret'],
            cluster = settings.pusher['cluster'],
            ssl = True
        )

    def get_client(self):
        return self.pusher_client