from tests.common import ReclaimTestCase


class TestTaskSearch(ReclaimTestCase):
    """
    Tests the task search functionality, as there is none in the
    API and has to be done manually.
    """

    def test_search(self):
        """
        Search for a task by name.
        """

        self.test_task.save()
        tasks = self.test_task.search(
            title="test_task_12345",
        )

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].id, self.test_task.id)

        self.test_task.delete()
