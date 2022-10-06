from datetime import datetime, timedelta
from time import sleep

from tests.common import ReclaimTestCase


class TestScheduledDates(ReclaimTestCase):
    """
    Tests if the scheduled dates are computed
    correctly
    """

    def test_scheduled_dates(self):
        """
        Tests if the scheduled dates are computed
        correctly
        """

        with self.test_task as task:

            # Setting the start date to in 10 days
            task.start_date = datetime.now() + timedelta(days=10)
            # Setting the due date to in 15 days
            task.due_date = datetime.now() + timedelta(days=15)
            # Set the duration to 8 hours
            task.duration = 8

        # Checking if the scheduled dates are already set
        while not self.test_task.scheduled_end_date:
            self.test_task.update()
            sleep(5)
