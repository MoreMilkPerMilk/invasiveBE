import unittest
import uuid

import DatabaseService
import UserService
from Models.User import Person
from Models.WeedInstance import WeedInstance

client = DatabaseService.connect_to_mongodb()
db = client['test-user']


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        all_persons = UserService.get_all(db)
        for person in all_persons:
            UserService.delete_person_by_id(db, person.person_id)

        self.assertTrue(len(UserService.get_all(db)) == 0)

    def test_create_person(self):
        person = {
            "person_id": 0,
            "first_name": "Hamish",
            "last_name": "Bultitude",
            "date_joined": "2021-08-10",
            "count_identified": 40,
            "previous_tags": []
        }
        model = Person(**person)

        UserService.create_person(db, model)

        all_persons = UserService.get_all(db)
        self.assertTrue(len(all_persons) == 1)
        self.assertTrue(all_persons[0] == person)

    def test_get_person_by_id(self):
        person = {
            "person_id": 0,
            "first_name": "Hamish",
            "last_name": "Bultitude",
            "date_joined": "2021-08-10",
            "count_identified": 40,
            "previous_tags": []
        }
        model = Person(**person)
        UserService.create_person(db, model)

        got_person = UserService.get_person_by_id(db, model.person_id)
        self.assertTrue(got_person == model)

    def test_update_person_identifications(self):
        person = {
            "person_id": 0,
            "first_name": "Hamish",
            "last_name": "Bultitude",
            "date_joined": "2021-08-10",
            "count_identified": 40,
            "previous_tags": []
        }
        model = Person(**person)
        UserService.create_person(db, model)

        got_person = UserService.get_person_by_id(db, model.person_id)
        self.assertTrue(len(got_person.previous_tags) == 0)

        weed1 = {
            "uuid": uuid.uuid4(),
            "image_bytes": b'Image Data',
            "species_id": 78,
            "discovery_date": "2000-01-01",
            "removed": False,
            "replaced": False
        }
        weed1 = WeedInstance(**weed1)
        print(weed1)
        UserService.update_person_identifications(db, got_person.person_id, weed1)

        new_person = UserService.get_person_by_id(db, model.person_id)
        print(new_person)
        self.assertTrue(got_person != new_person)




if __name__ == '__main__':
    unittest.main()
