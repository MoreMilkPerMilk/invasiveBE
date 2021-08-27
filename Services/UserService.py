import DatabaseService
import pymongo

from typing import List, Optional
from pymongo.collection import Collection

from Models.Person import Person
from Models.WeedInstance import WeedInstance

def set_unique_keys(users_collection: Collection):
    """Sets users_collection to be uniquely identified by 'person_id' ASC"""
    users_collection.create_index(
        [("person_id", pymongo.ASCENDING)],
        unique=True
    )

def get_all(users_db: Collection) -> List[Person]:
    return [Person(**x) for x in users_db.find()]


def get_person_by_id(users_db: Collection, id: int) -> Optional[Person]:
    person = users_db.find_one({"person_id": id})
    if person is None:
        return None
    else:
        return Person(**person)

def create_person(users_db: Collection, person: Person) -> Person:
    """
    Create a new person. Return the old person if ID already present, and do not add new person.
    """
    previous_person = users_db.find_one({"person_id": person.person_id})
    if previous_person is None:
        users_db.insert_one(person.dict())
        return person
    else:
        return previous_person


def update_person_identifications(users_db: Collection, person_id: int, weed_instance: WeedInstance):
    key = {"person_id": person_id}
    person = Person(**users_db.find_one(key))
    person.add_identification(weed_instance)

    users_db.replace_one(key, person.dict(), upsert=True)


def delete_person_by_id(users_db: Collection, id: int):
    users_db.delete_many({"person_id": id})


# client = DatabaseService.connect_to_mongodb()
# db = client['users']
# person = {
#     "person_id": 0,
#     "first_name": "Hamish",
#     "last_name": "Bultitude",
#     "date_joined": "2021-08-10",
#     "count_identified": 40,
#     "previous_tags": []
# }
# person2 = {
#     "person_id": 1,
#     "first_name": "Joe",
#     "last_name": "Bloggs",
#     "date_joined": "2000-2-3",
#     "count_identified": 69,
#     "previous_tags": []
# }
# delete_person_by_id(db, person['person_id'])
# delete_person_by_id(db, person2['person_id'])
# create_person(db, Person(**person))
# create_person(db, Person(**person2))
# print(get_all(users_db=db))
# print(get_person_by_id(db, person['person_id']))

# weed1 = {
#     "species_id": 78,
#     "discovery_date": "2000-01-01",
#     "removed": False,
#     "replaced": False
# }
# update_person_identifications(db, person["person_id"], WeedInstance(**weed1))
# print(get_person_by_id(db, person['person_id']))

# get_person_by_id()
