"""Reclaim smart-meeting series resource.

Backs ``/api/smart-meetings`` — Reclaim's recurring, AI-scheduled meeting series.
Each series declares *when*, *how long*, and *with whom* meetings should be
defended on the calendar.

Supports full CRUD (GET / POST / PATCH / DELETE) via :class:`BaseResource`,
plus planner actions (lock, unlock, skip, reschedule, move) for individual
meeting instances.
"""

from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field

from reclaim_sdk.client import ReclaimClient
from reclaim_sdk.enums import (
    ConferenceType,
    DefenseAggression,
    Frequency,
    SmartSeriesEventType,
    SmartSeriesRecurrenceType,
    SmartSeriesStatus,
    SmartSeriesVisibility,
    TimePolicyType,
)
from reclaim_sdk.resources.base import BaseResource


# ---------------------------------------------------------------------------
# Nested models
# ---------------------------------------------------------------------------


class _CamelModel(BaseModel):
    """Shared config: camelCase aliases, allow forward-compatible extra keys."""

    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }


class AttendeeInfo(_CamelModel):
    """Attendee identity info."""

    user_id: Optional[str] = Field(None, alias="userId")
    email: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    reclaim_user: bool = Field(False, alias="reclaimUser")


class TimezoneInfo(_CamelModel):
    """Timezone info for an attendee."""

    id: Optional[str] = None
    display_name: Optional[str] = Field(None, alias="displayName")
    abbreviation: Optional[str] = None


class ConferenceDetails(_CamelModel):
    """Conference details (Zoom/Meet URL, etc.)."""

    solution: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None


class SmartSeriesAttendee(_CamelModel):
    """A single attendee of a smart-meeting series."""

    attendee: Optional[AttendeeInfo] = None
    required: bool = False
    role: Optional[str] = None
    timezone: Optional[TimezoneInfo] = None
    time_policy_type: Optional[TimePolicyType] = Field(
        None, alias="timePolicyType"
    )
    time_scheme_id: Optional[str] = Field(None, alias="timeSchemeId")
    one_off_policy: Optional[Dict[str, Any]] = Field(
        None, alias="oneOffPolicy"
    )
    priority: Optional[str] = None
    response_status: Optional[str] = Field(None, alias="responseData")


class Organizer(_CamelModel):
    """Organizer config for creating/updating a smart meeting.

    The web app transforms this to ``{timePolicyType, timeSchemeId,
    oneOffPolicy, priority}`` — email is *not* sent.
    """

    time_policy_type: Optional[TimePolicyType] = Field(
        None, alias="timePolicyType"
    )
    time_scheme_id: Optional[str] = Field(None, alias="timeSchemeId")
    one_off_policy: Optional[Dict[str, Any]] = Field(
        None, alias="oneOffPolicy"
    )
    priority: Optional[str] = None


class RecurrenceDefinition(_CamelModel):
    """Recurrence definition for a smart-meeting series."""

    frequency: Optional[Frequency] = None
    interval: Optional[int] = None
    ideal_days: Optional[List[str]] = Field(None, alias="idealDays")
    ideal_monthly_day: Optional[Dict[str, Any]] = Field(
        None, alias="idealMonthlyDay"
    )
    days_between_periods: Optional[int] = Field(None, alias="daysBetweenPeriods")


class SmartSeriesView(_CamelModel):
    """A single smart-meeting series (the ``activeSeries`` or ``series``
    object returned by the API)."""

    id: Optional[int] = None
    event_id: Optional[str] = Field(None, alias="eventId")
    title: Optional[str] = None
    starting: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    ending: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    ideal_time: Optional[str] = Field(None, alias="idealTime")
    min_duration_mins: Optional[int] = Field(None, alias="durationMinMins")
    max_duration_mins: Optional[int] = Field(None, alias="durationMaxMins")
    recurrence: Optional[RecurrenceDefinition] = None
    color: Optional[str] = None
    attendees: Optional[List[SmartSeriesAttendee]] = None
    description: Optional[str] = None
    location: Optional[str] = None
    google_meet: Optional[bool] = Field(None, alias="googleMeet")
    conference_details: Optional[ConferenceDetails] = Field(
        None, alias="conferenceDetails"
    )
    resources: Optional[List[Dict[str, Any]]] = None
    event_type: Optional[SmartSeriesEventType] = Field(
        None, alias="eventType"
    )
    defense_aggression: Optional[DefenseAggression] = Field(
        None, alias="defenseAggression"
    )
    visibility: Optional[SmartSeriesVisibility] = None
    defended_description: Optional[str] = Field(None, alias="defendedDescription")
    auto_decline: Optional[bool] = Field(None, alias="autoDecline")
    auto_decline_text: Optional[str] = Field(None, alias="autoDeclineText")
    dependency_type: Optional[str] = Field(None, alias="dependencyType")
    dependency_ref: Optional[int] = Field(None, alias="dependencyRef")
    reserved_words: Optional[List[str]] = Field(None, alias="reservedWords")
    failure_policy: Optional[str] = Field(None, alias="failurePolicy")
    fixed_time_policy: Optional[bool] = Field(None, alias="fixedTimePolicy")
    reschedule_unstarted_override: Optional[bool] = Field(
        None, alias="rescheduleUnstartedOverride"
    )
    recurrence_type: Optional[SmartSeriesRecurrenceType] = Field(
        None, alias="recurrenceType"
    )
    reminders: Optional[List[int]] = None
    calendar_id: Optional[int] = Field(None, alias="calendarId")
    status: Optional[str] = None
    conference_type: Optional[ConferenceType] = Field(
        None, alias="conferenceType"
    )
    guests_can_modify: Optional[bool] = Field(None, alias="guestsCanModify")


class SmartSeriesPeriodEvent(_CamelModel):
    """Event object inside a period."""

    id: Optional[str] = None
    title: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None


class SmartSeriesPeriodView(_CamelModel):
    """A single scheduled period (instance) of a smart-meeting series."""

    event_key: Optional[str] = Field(None, alias="eventKey")
    series_id: Optional[int] = Field(None, alias="seriesId")
    start: Optional[str] = None
    end: Optional[str] = None
    done: bool = False
    locked: bool = False
    force_skipped: bool = Field(False, alias="forceSkipped")
    scheduler_skipped: bool = Field(False, alias="schedulerSkipped")
    scheduler_status: Optional[str] = Field(None, alias="schedulerStatus")
    event_status: Optional[str] = Field(None, alias="eventStatus")
    event_start: Optional[str] = Field(None, alias="eventStart")
    event_end: Optional[str] = Field(None, alias="eventEnd")
    has_time_policy_exceptions: bool = Field(
        False, alias="hasTimePolicyExceptions"
    )
    target_date_time: Optional[str] = Field(None, alias="targetDateTime")
    changes: Optional[Any] = None
    event: Optional[SmartSeriesPeriodEvent] = None


class SmartMeetingLineageView(_CamelModel):
    """Response wrapper for a single smart-meeting lineage entry.

    Returned by ``GET /api/smart-meetings`` and
    ``GET /api/smart-meetings/{lineageId}``.
    """

    lineage_id: Optional[int] = Field(None, alias="lineageId")
    calendar_id: Optional[int] = Field(None, alias="calendarId")
    type: Optional[str] = None
    status: Optional[str] = None
    active_series: Optional[SmartSeriesView] = Field(
        None, alias="activeSeries"
    )
    series: Optional[List[SmartSeriesView]] = None
    periods: Optional[List[SmartSeriesPeriodView]] = None
    enabled: Optional[bool] = None
    restorable: Optional[bool] = None
    recurrence_type: Optional[SmartSeriesRecurrenceType] = Field(
        None, alias="recurrenceType"
    )


# ---------------------------------------------------------------------------
# Planner action result
# ---------------------------------------------------------------------------


class SmartSeriesActionPlannedResult(_CamelModel):
    """Result of a planner action (lock, unlock, skip, reschedule, move)."""

    events: Optional[List[Dict[str, Any]]] = None
    series: Optional[SmartSeriesView] = None
    user_info_message: Optional[str] = Field(None, alias="userInfoMessage")
    timeout_reached: bool = Field(False, alias="timeoutReached")


# ---------------------------------------------------------------------------
# Request models (for create / patch)
# ---------------------------------------------------------------------------


class CreateSmartMeetingRequest(_CamelModel):
    """Payload for ``POST /api/smart-meetings``.

    **Note**: The Reclaim API does not support adding attendees during
    creation — the organizer is automatically added as the sole attendee.
    Additional attendees must be added manually in the Reclaim web app.
    Sending ``attendees`` in the create request will result in a 400 error.
    """

    title: str
    enabled: bool = True
    event_type: SmartSeriesEventType = Field(
        ..., alias="eventType"
    )
    ideal_time: str = Field(..., alias="idealTime")
    duration_min_mins: int = Field(..., alias="durationMinMins")
    defense_aggression: DefenseAggression = Field(
        ..., alias="defenseAggression"
    )
    organizer: Organizer = Field(default_factory=Organizer)
    recurrence: Optional[RecurrenceDefinition] = None
    starting: Optional[str] = Field(
        None, description="Start date (YYYY-MM-DD)"
    )
    ending: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    duration_max_mins: Optional[int] = Field(None, alias="durationMaxMins")
    description: Optional[str] = None
    location: Optional[str] = None
    conference_type: Optional[ConferenceType] = Field(
        None, alias="conferenceType"
    )
    visibility: Optional[SmartSeriesVisibility] = None
    auto_decline: Optional[bool] = Field(None, alias="autoDecline")
    auto_decline_text: Optional[str] = Field(None, alias="autoDeclineText")
    defense_description: Optional[str] = Field(None, alias="defendedDescription")
    calendar_id: Optional[int] = Field(None, alias="calendarId")
    attendees: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    failure_policy: Optional[str] = Field(None, alias="failurePolicy")
    min_lead_time_mins: Optional[int] = Field(None, alias="minLeadTimeMins")
    fixed_time_policy: Optional[bool] = Field(None, alias="fixedTimePolicy")
    dependency_type: Optional[str] = Field(None, alias="dependencyType")
    dependency_ref: Optional[int] = Field(None, alias="dependencyRef")


class PatchSmartMeetingRequest(_CamelModel):
    """Payload for ``PATCH /api/smart-meetings/{lineageId}``.

    All fields are optional — only provided fields are sent.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    recurrence: Optional[RecurrenceDefinition] = None
    starting: Optional[str] = None
    ending: Optional[str] = None
    ideal_time: Optional[str] = Field(None, alias="idealTime")
    duration_min_mins: Optional[int] = Field(None, alias="durationMinMins")
    duration_max_mins: Optional[int] = Field(None, alias="durationMaxMins")
    event_type: Optional[SmartSeriesEventType] = Field(
        None, alias="eventType"
    )
    color: Optional[str] = None
    defense_aggression: Optional[DefenseAggression] = Field(
        None, alias="defenseAggression"
    )
    visibility: Optional[SmartSeriesVisibility] = None
    defended_description: Optional[str] = Field(None, alias="defendedDescription")
    auto_decline: Optional[bool] = Field(None, alias="autoDecline")
    auto_decline_text: Optional[str] = Field(None, alias="autoDeclineText")
    organizer: Optional[Organizer] = None
    attendees: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    location: Optional[str] = None
    conference_type: Optional[ConferenceType] = Field(
        None, alias="conferenceType"
    )
    calendar_id: Optional[int] = Field(None, alias="calendarId")
    failure_policy: Optional[str] = Field(None, alias="failurePolicy")
    min_lead_time_mins: Optional[int] = Field(None, alias="minLeadTimeMins")
    fixed_time_policy: Optional[bool] = Field(None, alias="fixedTimePolicy")


# ---------------------------------------------------------------------------
# Main resource
# ---------------------------------------------------------------------------


class SmartMeeting(BaseResource):
    """A Reclaim smart-meeting series.

    Full CRUD against ``/api/smart-meetings`` plus planner actions on
    individual instances.

    The editable series fields (title, durations, recurrence, etc.) live on
    :class:`CreateSmartMeetingRequest` / :class:`PatchSmartMeetingRequest`,
    not on this resource — so create and update go through ``create()`` and
    ``update()`` rather than constructing/mutating the resource directly.

    Example usage::

        from reclaim_sdk.resources.smart_meeting import (
            SmartMeeting,
            CreateSmartMeetingRequest,
            PatchSmartMeetingRequest,
            Organizer,
            RecurrenceDefinition,
        )
        from reclaim_sdk.enums import (
            SmartSeriesEventType,
            DefenseAggression,
            TimePolicyType,
            Frequency,
            SnoozeOption,
        )

        # List all smart meetings
        meetings = SmartMeeting.list()

        # Get a single meeting
        meeting = SmartMeeting.get(4559766)

        # Create a new smart meeting
        meeting = SmartMeeting.create(
            CreateSmartMeetingRequest(
                title="Weekly Sync",
                event_type=SmartSeriesEventType.TEAM_MEETING,
                ideal_time="10:00:00",
                duration_min_mins=30,
                defense_aggression=DefenseAggression.DEFAULT,
                organizer=Organizer(time_policy_type=TimePolicyType.WORK),
                recurrence=RecurrenceDefinition(
                    frequency=Frequency.WEEKLY,
                    ideal_days=["MONDAY", "WEDNESDAY", "FRIDAY"],
                    interval=2,
                ),
            )
        )

        # Update (PATCH) — send only the fields that change
        meeting.update(PatchSmartMeetingRequest(title="Biweekly Sync"))

        # Delete
        meeting.delete()

        # Planner actions (instance-level)
        meeting.lock()
        meeting.unlock()
        meeting.skip()
        meeting.reschedule(SnoozeOption.NEXT_WEEK)
        meeting.move(start, end)
        meeting.clear_exceptions()
    """

    ENDPOINT: ClassVar[str] = "/api/smart-meetings"

    lineage_id: Optional[int] = Field(None, alias="lineageId")
    calendar_id: Optional[int] = Field(None, alias="calendarId")
    type: Optional[str] = None
    status: Optional[SmartSeriesStatus] = None
    active_series: Optional[SmartSeriesView] = Field(
        None, alias="activeSeries"
    )
    series: Optional[List[SmartSeriesView]] = None
    periods: Optional[List[SmartSeriesPeriodView]] = None
    enabled: Optional[bool] = None
    restorable: Optional[bool] = None
    recurrence_type: Optional[SmartSeriesRecurrenceType] = Field(
        None, alias="recurrenceType"
    )

    @classmethod
    def from_api_data(cls, data: Dict) -> "SmartMeeting":
        """Override to handle lineageId as the primary ID."""
        instance = super().from_api_data(data)
        # Use lineageId as the resource ID for CRUD operations
        if instance.lineage_id is not None:
            instance.id = instance.lineage_id
        return instance

    def to_api_data(self) -> Dict:
        """Exclude lineageId from create/patch payloads — it's server-assigned."""
        data = super().to_api_data()
        # Remove both snake_case and alias forms
        data.pop("lineage_id", None)
        data.pop("lineageId", None)
        return data

    def update(self, request: PatchSmartMeetingRequest) -> "SmartMeeting":
        """PATCH the editable fields of this series.

        The editable fields (title, durations, recurrence, etc.) live on
        :class:`PatchSmartMeetingRequest`, not on the resource itself — so
        updates go through this method rather than attribute assignment +
        ``save()``. Only set (non-None) fields are sent. The server response
        refreshes this instance in place.

        Args:
            request: A :class:`PatchSmartMeetingRequest` with the changes.
        """
        if self.id is None:
            raise ValueError(
                "Cannot update a smart meeting without a lineageId. "
                "Fetch it with SmartMeeting.get() first."
            )
        response = self._client.patch(
            f"{self.ENDPOINT}/{self.id}",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        self.__dict__.update(self.from_api_data(response).__dict__)
        return self

    # ------------------------------------------------------------------
    # Planner actions
    # ------------------------------------------------------------------

    def _get_event_id(self) -> Optional[str]:
        """Return the eventId string needed for instance-level planner actions.

        The eventId is found in ``activeSeries.eventId``.
        """
        if self.active_series and self.active_series.event_id:
            return self.active_series.event_id
        return None

    def lock(self) -> SmartSeriesActionPlannedResult:
        """Lock a meeting instance so Reclaim won't move it."""
        event_id = self._get_event_id()
        if not event_id:
            raise ValueError(
                "Cannot lock: no eventId found. "
                "Fetch the meeting with SmartMeeting.get() first."
            )
        response = self._client.post(
            f"{self.ENDPOINT}/planner/{event_id}/lock"
        )
        return SmartSeriesActionPlannedResult.model_validate(response)

    def unlock(self) -> SmartSeriesActionPlannedResult:
        """Unlock a previously-locked meeting instance."""
        event_id = self._get_event_id()
        if not event_id:
            raise ValueError(
                "Cannot unlock: no eventId found. "
                "Fetch the meeting with SmartMeeting.get() first."
            )
        response = self._client.post(
            f"{self.ENDPOINT}/planner/{event_id}/unlock"
        )
        return SmartSeriesActionPlannedResult.model_validate(response)

    def skip(self) -> SmartSeriesActionPlannedResult:
        """Skip the next scheduled instance of this series."""
        event_id = self._get_event_id()
        if not event_id:
            raise ValueError(
                "Cannot skip: no eventId found. "
                "Fetch the meeting with SmartMeeting.get() first."
            )
        response = self._client.post(
            f"{self.ENDPOINT}/planner/{event_id}/skip"
        )
        return SmartSeriesActionPlannedResult.model_validate(response)

    def reschedule(
        self,
        snooze_option: str,
    ) -> SmartSeriesActionPlannedResult:
        """Reschedule the next instance using a snooze option.

        Args:
            snooze_option: A ``SnoozeOption`` enum value (string).
        """
        from reclaim_sdk.enums import SnoozeOption

        if isinstance(snooze_option, SnoozeOption):
            snooze_option = snooze_option.value
        event_id = self._get_event_id()
        if not event_id:
            raise ValueError(
                "Cannot reschedule: no eventId found. "
                "Fetch the meeting with SmartMeeting.get() first."
            )
        response = self._client.post(
            f"{self.ENDPOINT}/planner/{event_id}/reschedule",
            params={"snoozeOption": snooze_option},
        )
        return SmartSeriesActionPlannedResult.model_validate(response)

    def move(
        self,
        start: datetime,
        end: datetime,
    ) -> SmartSeriesActionPlannedResult:
        """Move a meeting instance to a new time.

        Args:
            start: New start time (UTC).
            end: New end time (UTC).
        """
        event_id = self._get_event_id()
        if not event_id:
            raise ValueError(
                "Cannot move: no eventId found. "
                "Fetch the meeting with SmartMeeting.get() first."
            )
        response = self._client.post(
            f"{self.ENDPOINT}/planner/{event_id}/move",
            params={
                "start": start.isoformat().replace("+00:00", "Z"),
                "end": end.isoformat().replace("+00:00", "Z"),
            },
        )
        return SmartSeriesActionPlannedResult.model_validate(response)

    def clear_exceptions(self) -> SmartSeriesActionPlannedResult:
        """Reset schedule — clear all exceptions for this series."""
        response = self._client.post(
            f"{self.ENDPOINT}/planner/{self.lineage_id}/clear-exceptions"
        )
        return SmartSeriesActionPlannedResult.model_validate(response)

    # ------------------------------------------------------------------
    # Class-level convenience methods
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        request: CreateSmartMeetingRequest,
        send_updates: bool = False,
        client: ReclaimClient = None,
    ) -> "SmartMeeting":
        """Create a new smart-meeting series.

        Args:
            request: A :class:`CreateSmartMeetingRequest` with the series config.
            send_updates: Whether to send update notifications to attendees.
            client: Optional ReclaimClient override.
        """
        if client is None:
            client = ReclaimClient()
        params = {"sendUpdates": send_updates}
        data = client.post(
            cls.ENDPOINT,
            params=params,
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return cls.from_api_data(data)

    @classmethod
    def detect(cls, client: ReclaimClient = None) -> List["SmartMeeting"]:
        """Detect smart meetings that could be created from existing events.

        Returns:
            List of detected smart meetings.
        """
        if client is None:
            client = ReclaimClient()
        data = client.get(f"{cls.ENDPOINT}/detect")
        return [cls.from_api_data(item) for item in (data or [])]

    @classmethod
    def convert_to_smart_meetings(
        cls,
        calendar_id: int,
        event_id: str,
        request: CreateSmartMeetingRequest,
        client: ReclaimClient = None,
    ) -> "SmartMeeting":
        """Convert an existing calendar event into a smart-meeting series.

        Args:
            calendar_id: The calendar ID.
            event_id: The existing event ID.
            request: Smart meeting configuration.
            client: Optional ReclaimClient override.
        """
        if client is None:
            client = ReclaimClient()
        data = client.post(
            f"{cls.ENDPOINT}/convert/{calendar_id}/{event_id}",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )
        return cls.from_api_data(data)

    @classmethod
    def convert_to_single_instances(
        cls,
        lineage_id: int,
        client: ReclaimClient = None,
    ) -> List["SmartMeeting"]:
        """Convert a smart-meeting series back to single instances.

        Args:
            lineage_id: The smart meeting lineage ID.
            client: Optional ReclaimClient override.
        """
        if client is None:
            client = ReclaimClient()
        data = client.post(
            f"{cls.ENDPOINT}/to-single-instances",
            params={"lineageId": lineage_id},
        )
        return [cls.from_api_data(item) for item in (data or [])]

    @classmethod
    def find_attendee_declined(
        cls, client: ReclaimClient = None
    ) -> List["SmartMeeting"]:
        """List smart meetings where an attendee declined.

        Args:
            client: Optional ReclaimClient override.
        """
        if client is None:
            client = ReclaimClient()
        data = client.get(f"{cls.ENDPOINT}/attendeeDeclined")
        return [cls.from_api_data(item) for item in (data or [])]

    @classmethod
    def invite_organizer(
        cls,
        lineage_ids: List[int],
        client: ReclaimClient = None,
    ) -> Dict[str, Any]:
        """Invite an organizer to create a smart-meeting series.

        Args:
            lineage_ids: List of lineage IDs to invite for.
            client: Optional ReclaimClient override.
        """
        if client is None:
            client = ReclaimClient()
        return client.post(
            f"{cls.ENDPOINT}/invite-organizer",
            params={"lineageIds": lineage_ids},
        )
