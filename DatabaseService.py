import json
import pymongo

def connect_to_mongodb():
    with open('cred.json') as f:
        cred = json.load(f)
        user = cred['user']
        password = cred['password']
        url = cred['url']
        client = pymongo.MongoClient(url.replace('<password>', password))
        return client['data']
