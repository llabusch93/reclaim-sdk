from datetime import datetime

from reclaim_sdk.client import ReclaimAPICall
from reclaim_sdk.models.model import ReclaimModel
from reclaim_sdk.utils import to_datetime, from_datetime


class ReclaimTaskEvent(ReclaimModel):
    """
    Task events are a special case, as they cannot be created by the user.
    They are created by the API when a task is scheduled. The user can only
    update the start and end times of the event, pin the event or delete it.
    """

    _name = "Task Event"
    _required_fields = ["start", "end"]
    _endpoint = "/api/planner/event/move"

    def __init__(self, data: dict, task, **kwargs) -> None:
        super().__init__(data, **kwargs)
        self.task = task

    @property
    def id(self):
        return self._data.get("eventId", None)

    @property
    def start(self) -> datetime:
        return to_datetime(self["start"])

    @start.setter
    def start(self, value: datetime):
        self._data["start"] = from_datetime(value)

    @property
    def end(self) -> datetime:
        return to_datetime(self["end"])

    @end.setter
    def end(self, value: datetime):
        self._data["end"] = from_datetime(value)

    def _create(self, **kwargs):
        """
        Task Events cannot be created by the user.
        """
        raise NotImplementedError("Task Events cannot be created by the user.")

    def delete(self, **kwargs):
        """
        Task Event cannot be deleted by the user.
        """
        raise NotImplementedError("Task Events cannot be deleted by the user.")

    def _update(self, **kwargs):
        """
        Updates the task event. Only the start and end times (event move).
        """
        params = {
            **kwargs,
            "start": self["start"],
            "end": self["end"],
        }
        with ReclaimAPICall(self) as client:
            res = client.post(
                f"{self._endpoint}/{self.id}",
                params=params,
            )
            res.raise_for_status()

        self._data = res.json()["events"][0]
