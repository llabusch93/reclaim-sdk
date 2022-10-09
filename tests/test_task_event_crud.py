from datetime import datetime, timedelta
from time import sleep

from tests.common import ReclaimTestCase


class TestTaskEventCRUD(ReclaimTestCase):
    """
    Tests the CRUD operations of the Task Event model, what is basically
    only the update and delete operation as the task events are created
    automatically by the API.
    """

    def test_task_event_update_delete(self):
        """
        Tests the update and delete operations of a task event.
        """
        with self.test_task as task:

            # Setting the start date to in 10 days
            task.start_date = datetime.now() + timedelta(days=10)
            # Setting the due date to in 15 days
            task.due_date = datetime.now() + timedelta(days=15)
            # Set the duration to 8 hours
            task.duration = 8

        # Wait until the task got scheduled
        while not self.test_task.scheduled_end_date:
            self.test_task.update()
            sleep(5)

        # We change the end date of the first task event to 1 hour after the
        # scheduled end date (so the time span gets extended by 1 hour)
        event_duration_before = (
            self.test_task.events[0].end - self.test_task.events[0].start
        )
        with self.test_task.events[0] as event:
            event.end = event.end + timedelta(hours=1)

        event_duration_after = (
            self.test_task.events[0].end - self.test_task.events[0].start
        )

        # The duration of the event should have increased by 1 hour
        self.assertEqual(
            event_duration_after, event_duration_before + timedelta(hours=1)
        )
