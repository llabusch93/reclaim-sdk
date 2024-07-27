from __future__ import annotations
from pydantic import Field, field_validator
from datetime import datetime
from typing import ClassVar, Optional
from enum import Enum
from reclaim_sdk.resources.base import BaseResource


class PriorityEnum(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TaskStatus(str, Enum):
    NEW = "NEW"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class EventCategory(str, Enum):
    WORK = "WORK"
    PERSONAL = "PERSONAL"


class Task(BaseResource):
    ENDPOINT: ClassVar[str] = "/api/tasks"

    title: Optional[str] = Field(None, description="Task title")
    notes: Optional[str] = Field(None, description="Task notes")
    eventCategory: EventCategory = Field(
        default=EventCategory.WORK, description="Event category"
    )
    eventSubType: Optional[str] = Field(None, description="Event subtype")
    timeSchemeId: Optional[str] = Field(None, description="Time scheme ID (custom hours)")
    timeChunksRequired: Optional[int] = Field(None, description="Time chunks required")
    minChunkSize: Optional[int] = Field(None, description="Minimum chunk size")
    maxChunkSize: Optional[int] = Field(None, description="Maximum chunk size")
    priority: PriorityEnum = Field(None, description="Task priority")
    onDeck: bool = Field(False, description="Task is on deck")
    alwaysPrivate: bool = Field(False, description="Task is always private")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    due: Optional[datetime] = Field(None, description="Due date")
    snoozeUntil: Optional[datetime] = Field(None, description="Snooze until date")
    index: Optional[float] = Field(None, description="Task index")

    @field_validator(
        "timeChunksRequired", "minChunkSize", "maxChunkSize", mode="before"
    )
    @classmethod
    def validate_chunks(cls, v):
        if v is not None:
            return int(v)
        return v

    @property
    def duration(self) -> Optional[float]:
        return self.timeChunksRequired / 4 if self.timeChunksRequired else None

    @duration.setter
    def duration(self, hours: float) -> None:
        self.timeChunksRequired = int(hours * 4)

    @property
    def min_work_duration(self) -> Optional[float]:
        return self.minChunkSize / 4 if self.minChunkSize else None

    @min_work_duration.setter
    def min_work_duration(self, hours: float) -> None:
        self.minChunkSize = int(hours * 4)

    @property
    def max_work_duration(self) -> Optional[float]:
        return self.maxChunkSize / 4 if self.maxChunkSize else None

    @max_work_duration.setter
    def max_work_duration(self, hours: float) -> None:
        self.maxChunkSize = int(hours * 4)

    @property
    def up_next(self) -> bool:
        return self.onDeck

    @up_next.setter
    def up_next(self, value: bool) -> None:
        self.onDeck = value

    def mark_complete(self) -> None:
        response = self._client.post(f"/api/planner/done/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])

    def mark_incomplete(self) -> None:
        response = self._client.post(f"/api/planner/unarchive/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])

    @classmethod
    def prioritize_by_due(cls) -> None:
        cls._client.patch("/api/tasks/reindex-by-due")

    def prioritize(self) -> None:
        self._client.post(f"/api/planner/prioritize/task/{self.id}")
        self.refresh()

    def add_time(self, hours: float) -> None:
        minutes = int(hours * 60)
        rounded_minutes = round(minutes / 15) * 15
        response = self._client.post(
            f"/api/planner/add-time/task/{self.id}", params={"minutes": rounded_minutes}
        )
        self.from_api_data(response["taskOrHabit"])

    def clear_exceptions(self) -> None:
        response = self._client.post(f"/api/planner/clear-exceptions/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])

    def log_work(self, minutes: int, end: Optional[datetime] = None) -> None:
        params = {"minutes": minutes}
        if end:
            params["end"] = end.isoformat()
        response = self._client.post(
            f"/api/planner/log-work/task/{self.id}", params=params
        )
        self.from_api_data(response["taskOrHabit"])

    def start(self) -> None:
        response = self._client.post(f"/api/planner/start/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])

    def stop(self) -> None:
        response = self._client.post(f"/api/planner/stop/task/{self.id}")
        self.from_api_data(response["taskOrHabit"])
