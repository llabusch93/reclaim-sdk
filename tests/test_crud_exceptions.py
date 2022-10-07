from tests.common import ReclaimTestCase
from reclaim_sdk.exceptions import RecordNotFound, InvalidRecord


class TestCrudExceptions(ReclaimTestCase):
    """
    Tests if the exceptions for the CRUD operations are raised correctly.
    """

    def test_get_wrong_id(self):
        """
        Tests the behavior of the get method when the id is wrong.
        """
        with self.assertRaises(RecordNotFound):
            self.test_task.get(0)

    def test_save_wrong_id(self):
        """
        Tests the behavior of the save method when the id is wrong.
        """
        with self.assertRaises(RecordNotFound):
            self.test_task._data["id"] = 0
            self.test_task.save()

    def test_save_missing_required_field(self):
        """
        Tests the behavior of the save method when a required field is missing.
        """
        with self.assertRaises(ValueError):
            self.test_task._data["title"] = ""
            self.test_task.save()

    def test_save_invalid_object(self):
        """
        Tests the behavior of the save method when the object is invalid.
        """

        with self.assertRaises(InvalidRecord):
            id = self.test_task.id
            # This is too less information so the API get an
            # Internal Server Error.
            self.test_task._data = {"id": id, "title": "Test Task"}
            self.test_task.save()
