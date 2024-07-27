from typing import ClassVar, Dict, List, Optional
from pydantic import Field
from reclaim_sdk.resources.base import BaseResource


class Hours(BaseResource):
    ENDPOINT: ClassVar[str] = "/api/timeschemes"

    id: str = Field(..., description="Unique identifier of the time scheme")
    status: str = Field(..., description="Status of the time scheme")
    task_category: Optional[str] = Field(
        None, alias="taskCategory", description="Task category"
    )
    task_target_calendar: Optional[Dict] = Field(
        None, alias="taskTargetCalendar", description="Target calendar for tasks"
    )
    title: str = Field(..., description="Title of the time scheme")
    description: str = Field(..., description="Description of the time scheme")
    features: List[str] = Field(
        ..., description="List of features associated with the time scheme"
    )

    class Config:
        alias_generator = None
        populate_by_name = True
