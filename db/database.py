import pymongo

# from ..config.settings import settings
from config.settings import settings

class database():
    def __init__(self) -> None:
        self.USER = settings.user 
        self.PASSWORD = settings.password 
        self.URL = settings.url
        self.client = None 

    def connect(self):
        if self.client is None: 
            self.client = pymongo.MongoClient(self.URL.replace("<password>", self.PASSWORD))
            
    def get_client(self) -> pymongo.MongoClient:
        self.connect()
        return self.client
