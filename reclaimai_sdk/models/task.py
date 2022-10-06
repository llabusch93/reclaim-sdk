from reclaimai_sdk.models.model import ReclaimModel
from reclaimai_sdk.utils import to_datetime, from_datetime
from datetime import datetime


class ReclaimTask(ReclaimModel):
    _endpoint = "/api/tasks"
    _name = "Task"
    _default_params = {
        # Only non archived tasks
        "status": "NEW,SCHEDULED,IN_PROGRESS,COMPLETE",
        # Get the scheduled planner events as well
        "instances": True,
    }

    # The required fields for a task to submit
    # to the API. The tuple second element is
    # the default value for the field.
    _required_fields = [
        ("title", None),
        ("eventCategory", "WORK"),
        ("minChunkSize", 2),  # Defaults to 30 minutes
        ("maxChunkSize", 8),  # Defaults to 2 hours
        ("timeChunksRequired", 8),  # Defaults to 2 hours
    ]

    @property
    def name(self) -> str:
        return self["title"]

    @name.setter
    def name(self, value: str) -> None:
        self["title"] = value

    @property
    def description(self) -> str:
        return self["notes"]

    @description.setter
    def description(self, value: str) -> None:
        self["notes"] = value

    @property
    def is_work_task(self) -> bool:
        return (self["eventCategory"] or "") == "WORK"

    @is_work_task.setter
    def is_work_task(self, value: bool) -> None:
        self["eventCategory"] = "WORK" if value else "PERSONAL"

    @property
    def is_private(self) -> bool:
        return self["alwaysPrivate"]

    @property
    def is_scheduled(self) -> bool:
        """
        Returns true if the task is scheduled.
        """
        status = self["status"] or ""
        return (status == "SCHEDULED") or (status == "IN_PROGRESS")

    @is_private.setter
    def is_private(self, value: bool):
        self["alwaysPrivate"] = value

    @property
    def update_date(self) -> datetime:
        return to_datetime(self["updated"])

    @property
    def create_date(self) -> datetime:
        return to_datetime(self["created"])

    @property
    def due_date(self) -> datetime:
        """
        Gets the due date of the task and returns it as a datetime object.
        The timezone is UTC.
        """
        due_date = self["due"]
        if due_date:
            return to_datetime(due_date)
        return None

    @due_date.setter
    def due_date(self, value: datetime) -> None:
        """
        Sets the due date of the task.
        """
        if isinstance(value, str):
            self["due"] = value
        else:
            self["due"] = from_datetime(value)

    @property
    def start_date(self) -> datetime:
        """
        Gets the not before date of the task and returns it as a datetime object.
        The timezone is UTC.
        """
        not_before = self["snoozeUntil"]
        if not_before:
            return to_datetime(not_before)
        return None

    @start_date.setter
    def start_date(self, value: datetime) -> None:
        """
        Sets the not before date of the task.
        """
        if isinstance(value, str):
            self["snoozeUntil"] = value
        else:
            self["snoozeUntil"] = from_datetime(value)

    @property
    def min_work_duration(self) -> int:
        """
        Gets the minimum duration of the task working chunks in hours.
        One working chunk is 15 minutes, so 4 working chunks are 1 hour.
        """
        working_chunks = self["minChunkSize"]
        if working_chunks:
            return working_chunks / 4
        return None

    @min_work_duration.setter
    def min_work_duration(self, value: int) -> None:
        """
        Sets the minimum duration of the task working chunks in hours.
        One working chunk is 15 minutes, so 4 working chunks are 1 hour.
        """
        self["minChunkSize"] = value * 4

    @property
    def max_work_duration(self) -> int:
        """
        Gets the maximum duration of the task working chunks in hours.
        One working chunk is 15 minutes, so 4 working chunks are 1 hour.
        """
        working_chunks = self["maxChunkSize"]
        if working_chunks:
            return working_chunks / 4
        return None

    @max_work_duration.setter
    def max_work_duration(self, value: int) -> None:
        """
        Sets the maximum duration of the task working chunks in hours.
        One working chunk is 15 minutes, so 4 working chunks are 1 hour.
        """
        self["maxChunkSize"] = value * 4

    @property
    def duration(self) -> int:
        """
        Gets the duration of the task in hours.
        """
        duration = self["timeChunksRequired"]
        if duration:
            return duration / 4
        return None

    @duration.setter
    def duration(self, value: int) -> None:
        """
        Sets the duration of the task in hours.
        """
        self["timeChunksRequired"] = value * 4

    @property
    def instances(self) -> list:
        """
        Gets the instances of the task.
        """
        return self["instances"]

    @property
    def scheduled_start_date(self) -> datetime:
        """
        Gets the scheduled start date of the task and returns it as a datetime
        object. The scheduled start date describes the date when the task is
        scheduled to start in the Reclaim.ai planner.
        The timezone is UTC.
        """
        if not self.is_scheduled or not self.instances:
            return None

        # Sort the instances by start date
        instances = sorted(self.instances, key=lambda x: x["start"])
        # Get the first instance
        instance = instances[0]
        # Get the start date
        start_date = instance["start"]
        return to_datetime(start_date)

    @property
    def scheduled_end_date(self) -> datetime:
        """
        Gets the scheduled end date of the task and returns it as a datetime
        object. The scheduled end date describes the date when the task is
        scheduled to end in the Reclaim.ai planner.
        The timezone is UTC.
        """
        if not self.is_scheduled or not self.instances:
            return None

        # Sort the instances by end date
        instances = sorted(self.instances, key=lambda x: x["end"])
        # Get the last instance
        instance = instances[-1]
        # Get the end date
        end_date = instance["end"]
        return to_datetime(end_date)

    def mark_complete(self) -> None:
        """
        Marks the task as complete.
        """
        url = f"{self._client._api_url}/api/planner/done/task/{self.id}"
        res = self._client.post(url)
        res.raise_for_status()

        self._data = res.json()["taskOrHabit"]

    def mark_incomplete(self) -> None:
        """
        Marks the task as incomplete.
        """
        url = f"{self._client._api_url}/api/planner/unarchive/task/{self.id}"
        res = self._client.post(url)
        res.raise_for_status()

        self._data = res.json()["taskOrHabit"]

    @classmethod
    def prioritize_by_due(cls) -> None:
        """
        Triggers the auto-prioritization of tasks at Reclaim.ai to sort them
        by due date.
        """
        url = f"{cls._client._api_url}/api/tasks/reindex-by-due"
        res = cls._client.patch(url)
        res.raise_for_status()
