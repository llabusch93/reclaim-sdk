from datetime import datetime

from reclaim_sdk.client import ReclaimAPICall
from reclaim_sdk.models.model import ReclaimModel
from reclaim_sdk.models.task_event import ReclaimTaskEvent
from reclaim_sdk.utils import from_datetime, to_datetime


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
    def id(self):
        return self._data.get("id", None)

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

    def _convert_to_timechunks(self, hours: int) -> int:
        """
        Converts the hours to time chunks and returns the number of
        time chunks rounded up.
        """
        return round((hours * 60) / 15)

    @property
    def min_work_duration(self) -> int:
        """
        Gets the minimum duration of the task working chunks in hours.
        """
        working_chunks = self["minChunkSize"]
        if working_chunks:
            return working_chunks / 4
        return None

    @min_work_duration.setter
    def min_work_duration(self, hours: float) -> None:
        """
        Sets the minimum duration of the task working chunks in hours.
        One working chunk is 15 minutes, so 4 working chunks are 1 hour.
        """
        self["minChunkSize"] = self._convert_to_timechunks(hours)

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
    def max_work_duration(self, hours: float) -> None:
        """
        Sets the maximum duration of the task working chunks in hours.
        One working chunk is 15 minutes, so 4 working chunks are 1 hour.
        """
        self["maxChunkSize"] = self._convert_to_timechunks(hours)

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
    def duration(self, hours: float) -> None:
        """
        Sets the duration of the task in hours.
        """
        self["timeChunksRequired"] = self._convert_to_timechunks(hours)

    @property
    def priority(self) -> int:
        """
        Gets the priority of the task. A lower value means higher priority.
        """
        return self["index"]

    @priority.setter
    def priority(self, value: int) -> None:
        """
        Sets the priority of the task. A lower value means higher priority.
        """
        self["index"] = value

    @property
    def events(self) -> list:
        """
        Parses and sets the task events, sorted by start date.
        """
        if not self["instances"]:
            return []

        events = []
        for event in self["instances"]:
            events.append(ReclaimTaskEvent(event, self))

        events = sorted(events, key=lambda x: x.start)

        return events

    @property
    def scheduled_start_date(self) -> datetime:
        """
        Gets the scheduled start date of the task and returns it as a datetime
        object. The scheduled start date describes the date when the task is
        scheduled to start in the Reclaim.ai planner.
        The timezone is UTC.
        """
        if not self.events:
            return None

        return self.events[0].start

    @property
    def scheduled_end_date(self) -> datetime:
        """
        Gets the scheduled end date of the task and returns it as a datetime
        object. The scheduled end date describes the date when the task is
        scheduled to end in the Reclaim.ai planner.
        The timezone is UTC.
        """
        if not self.events:
            return None

        return self.events[0].end

    def mark_complete(self) -> None:
        """
        Marks the task as complete.
        """
        with ReclaimAPICall(self) as client:
            url = f"{client._api_url}/api/planner/done/task/{self.id}"
            res = client.post(url)
            res.raise_for_status()

        self._data = res.json()["taskOrHabit"]

    def mark_incomplete(self) -> None:
        """
        Marks the task as incomplete.
        """
        with ReclaimAPICall(self) as client:
            url = f"{client._api_url}/api/planner/unarchive/task/{self.id}"
            res = client.post(url)
            res.raise_for_status()

        self._data = res.json()["taskOrHabit"]

    @classmethod
    def prioritize_by_due(cls) -> None:
        """
        Triggers the auto-prioritization of tasks at Reclaim.ai to sort them
        by due date.
        """
        with ReclaimAPICall(cls) as client:
            url = f"{client._api_url}/api/tasks/reindex-by-due"
            res = client.post(url)
            res.raise_for_status()

    def prioritize(self) -> None:
        """
        Sets the task on top of the task list.
        """
        with ReclaimAPICall(self) as client:
            url = f"{client._api_url}/api/planner/prioritize/task/{self.id}"
            res = client.post(url)
            res.raise_for_status()
