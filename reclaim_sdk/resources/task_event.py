from pydantic import Field, BaseModel, ConfigDict
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task


class TaskEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task: "Task" = Field(..., description="Task")
    start_time: datetime = Field(..., alias="startTime", description="Start time")
    end_time: datetime = Field(..., alias="endTime", description="End time")
