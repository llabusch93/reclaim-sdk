from tests.common import ReclaimTestCase
from httpx._exceptions import HTTPError


class TestTaskCRUD(ReclaimTestCase):
    def test_task_creation(self):
        """
        Tests the creation of a task at reclaim.ai
        """

        self.test_task.is_work_task = False
        self.assertTrue(self.test_task.id is not None)

        with self.test_task.postpone_save():
            # We set the date fields and the duration
            self.test_task.duration = 10
            self.test_task.start_date = "2050-01-01T07:00:00.000Z"
            self.test_task.due_date = "2050-01-31T17:00:00.000Z"
            self.test_task.min_work_duration = 0.75
            self.test_task.max_work_duration = 1.5
            self.test_task.description = "This is a test task"

        # We check if the task was saved correctly
        self.assertEqual(self.test_task.duration, 10)
        self.assertEqual(self.test_task.min_work_duration, 0.75)
        self.assertEqual(self.test_task.max_work_duration, 1.5)

        # Now we mark the task as complete
        self.test_task.mark_complete()
        self.assertEqual(self.test_task["status"], "ARCHIVED")

        # And we mark the task as incomplete again
        self.test_task.mark_incomplete()
        self.assertNotEqual(self.test_task["status"], "ARCHIVED")

        # We delete the task again and check if it was deleted
        task_id = self.test_task.id
        self.test_task.delete()

        # This should raise an 404 - Not Found error
        with self.assertRaises(HTTPError):
            self.test_task.get(task_id)
