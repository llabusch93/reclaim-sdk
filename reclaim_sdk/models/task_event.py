from datetime import datetime

from reclaim_sdk.models.model import ReclaimModel
from reclaim_sdk.utils import to_datetime


class ReclaimTaskEvent(ReclaimModel):
    """
    Task events are a special case, as they cannot be created by the user.
    They are created by the API when a task is scheduled. The user can only
    update the start and end times of the event, pin the event or delete it.
    """

    _name = "Task Event"
    _required_fields = ["start", "end"]

    def __init__(self, data: dict, task, **kwargs) -> None:
        super().__init__(data, **kwargs)
        self.task = task

    @property
    def id(self):
        return self._data.get("eventId", None)

    @property
    def start(self) -> datetime:
        return to_datetime(self["start"])

    @property
    def end(self) -> datetime:
        return to_datetime(self["end"])

    @property
    def pinned(self) -> bool:
        return self["pinned"]

    def _create(self, **kwargs):
        """
        Task Events cannot be created by the user.
        """
        raise NotImplementedError("Task Events cannot be created by the user.")

    def _update(self, **kwargs):
        """
        Updates the task event. Only the start and end times (event move) or
        pinned status (event pin) can be updated.
        """
        # TODO: Implement the special update logic for task events.
        raise NotImplementedError()

    def _delete(self, **kwargs):
        """
        Deletes the task event.
        """
        # TODO: Implement the special delete logic for task events.
        raise NotImplementedError()
