from unittest import TestCase

from reclaim_sdk.models.task import ReclaimTask


class ReclaimTestCase(TestCase):
    def setUp(self):
        super().setUp()

        with ReclaimTask(
            data={
                "title": "test_task_12345",
            }
        ) as task:
            self.test_task = task

    def tearDown(self):
        super().tearDown()
        self.clear_tasks()

    def clear_tasks(self):
        """
        Get all remaining test tasks and delete them.
        """
        test_tasks = ReclaimTask.search(
            title="test_task_12345",
        )

        for task in test_tasks:
            task.delete()
