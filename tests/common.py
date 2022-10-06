from unittest import TestCase

from reclaimai_sdk.models.task import ReclaimTask


class ReclaimTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        with ReclaimTask(
            data={
                "title": "test_task_12345",
            }
        ) as task:
            cls.test_task = task

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.clear_tasks()

    @classmethod
    def clear_tasks(cls):
        """
        Get all remaining test tasks and delete them.
        """
        test_tasks = ReclaimTask.search(
            title="test_task_12345",
        )

        for task in test_tasks:
            task.delete()
