"""Unit tests for the SmartMeeting resource.

Uses respx to mock HTTP calls — no live API access needed.
"""

import json

import httpx
import pytest
from datetime import datetime, timezone

from reclaim_sdk.enums import (
    DefenseAggression,
    Frequency,
    SmartSeriesEventType,
    SmartSeriesStatus,
    TimePolicyType,
)
from reclaim_sdk.resources.smart_meeting import (
    SmartMeeting,
    SmartSeriesView,
    CreateSmartMeetingRequest,
    PatchSmartMeetingRequest,
    Organizer,
    RecurrenceDefinition,
)


# ---------------------------------------------------------------------------
# Sample data (module-level constants to avoid fixture resolution issues)
# ---------------------------------------------------------------------------

SAMPLE_RESPONSE = {
    "lineageId": 4559766,
    "calendarId": 3177927,
    "type": "MEETING",
    "status": "ACTIVE",
    "enabled": True,
    "restorable": False,
    "activeSeries": {
        "id": 4742904,
        "eventId": "reclaim0meeting0o030o045597660o04742904",
        "title": "Weekly Sync",
        "starting": "2026-06-11",
        "idealTime": "14:00:00",
        "durationMinMins": 30,
        "durationMaxMins": 45,
        "eventType": "ONE_ON_ONE",
        "defenseAggression": "DEFAULT",
        "visibility": "DEFAULT",
        "description": "Regular sync",
        "autoDecline": False,
        "googleMeet": False,
        "conferenceDetails": {
            "solution": "ZOOM",
            "url": "https://us06web.zoom.us/j/123",
            "status": "UNKNOWN",
            "source": "PARSED",
        },
        "location": "https://us06web.zoom.us/j/123",
        "failurePolicy": "LEAVE_LAST_OR_RETURN_TO_ORIGINAL",
        "fixedTimePolicy": False,
        "recurrenceType": "RECURRING_SERIES",
        "status": "ACTIVE",
        "guestsCanModify": False,
        "attendees": [
            {
                "attendee": {
                    "userId": "abc-123",
                    "email": "user@example.com",
                    "name": "Test User",
                    "firstName": "Test",
                    "lastName": "User",
                    "avatarUrl": "https://example.com/avatar.png",
                    "reclaimUser": True,
                },
                "required": True,
                "role": "ORGANIZER",
                "timezone": {
                    "id": "America/Chicago",
                    "displayName": "Central Time",
                    "abbreviation": "CT",
                },
                "timePolicyType": "MEETING",
            }
        ],
    },
    "periods": [
        {
            "eventKey": "3177927/reclaim0meeting0o030o045597660o04559786_20260219T200000Z",
            "seriesId": 4742904,
            "start": "2026-02-19T20:00:00Z",
            "end": "2026-02-19T20:30:00Z",
            "done": False,
            "locked": False,
            "forceSkipped": False,
            "schedulerSkipped": False,
            "schedulerStatus": "NOT_SKIPPED",
            "eventStatus": "NONE",
            "eventStart": "2026-02-19T20:00:00Z",
            "eventEnd": "2026-02-19T20:30:00Z",
            "hasTimePolicyExceptions": False,
            "targetDateTime": "2026-02-19T20:00:00Z",
            "changes": {},
            "event": None,
        }
    ],
}


SAMPLE_LIST_RESPONSE = [
    {
        **SAMPLE_RESPONSE,
        "lineageId": 4559766,
        "activeSeries": {**SAMPLE_RESPONSE["activeSeries"], "title": "Weekly Sync"},
    },
    {
        **SAMPLE_RESPONSE,
        "lineageId": 4463792,
        "activeSeries": {**SAMPLE_RESPONSE["activeSeries"], "title": "Biweekly Standup"},
    },
]


# ---------------------------------------------------------------------------
# Tests — list
# ---------------------------------------------------------------------------


def test_list_returns_smart_meetings(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.get("/api/smart-meetings").mock(
        return_value=httpx.Response(200, json=SAMPLE_LIST_RESPONSE)
    )

    meetings = SmartMeeting.list()
    assert len(meetings) == 2
    assert meetings[0].lineage_id == 4559766
    assert meetings[0].id == 4559766  # lineageId becomes id
    assert meetings[1].lineage_id == 4463792
    assert meetings[1].status == SmartSeriesStatus.ACTIVE


def test_list_empty(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.get("/api/smart-meetings").mock(
        return_value=httpx.Response(200, json=[])
    )

    meetings = SmartMeeting.list()
    assert meetings == []


# ---------------------------------------------------------------------------
# Tests — get
# ---------------------------------------------------------------------------


def test_get_returns_single_meeting(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.get("/api/smart-meetings/4559766").mock(
        return_value=httpx.Response(200, json=SAMPLE_RESPONSE)
    )

    meeting = SmartMeeting.get(4559766)
    assert meeting.lineage_id == 4559766
    assert meeting.id == 4559766
    assert meeting.type == "MEETING"
    assert meeting.calendar_id == 3177927
    assert meeting.enabled is True
    assert meeting.restorable is False

    # activeSeries
    assert meeting.active_series is not None
    assert meeting.active_series.title == "Weekly Sync"
    assert meeting.active_series.event_id == "reclaim0meeting0o030o045597660o04742904"
    assert meeting.active_series.min_duration_mins == 30
    assert meeting.active_series.max_duration_mins == 45
    assert meeting.active_series.event_type == SmartSeriesEventType.ONE_ON_ONE
    assert meeting.active_series.defense_aggression == DefenseAggression.DEFAULT
    assert meeting.active_series.conference_details is not None
    assert meeting.active_series.conference_details.solution == "ZOOM"

    # attendees
    assert len(meeting.active_series.attendees) == 1
    attendee = meeting.active_series.attendees[0]
    assert attendee.role == "ORGANIZER"
    assert attendee.attendee.email == "user@example.com"
    assert attendee.attendee.first_name == "Test"
    assert attendee.attendee.last_name == "User"
    assert attendee.time_policy_type == TimePolicyType.MEETING

    # periods
    assert len(meeting.periods) == 1
    period = meeting.periods[0]
    assert period.series_id == 4742904
    assert period.done is False
    assert period.locked is False
    assert period.scheduler_status == "NOT_SKIPPED"


# ---------------------------------------------------------------------------
# Tests — create
# ---------------------------------------------------------------------------


def test_create_request_serializes_correctly():
    request = CreateSmartMeetingRequest(
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
    data = request.model_dump(by_alias=True, exclude_none=True)
    assert data["title"] == "Weekly Sync"
    assert data["eventType"] == "TEAM_MEETING"
    assert data["idealTime"] == "10:00:00"
    assert data["durationMinMins"] == 30
    assert data["defenseAggression"] == "DEFAULT"
    assert data["organizer"]["timePolicyType"] == "WORK"
    assert data["recurrence"]["frequency"] == "WEEKLY"
    assert data["recurrence"]["idealDays"] == ["MONDAY", "WEDNESDAY", "FRIDAY"]


def test_create_via_class_method(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.post("/api/smart-meetings").mock(
        return_value=httpx.Response(200, json={
            "lineageId": 9999999,
            "type": "MEETING",
            "status": "ACTIVE",
            "enabled": True,
            "activeSeries": {"title": "Weekly Sync", "eventId": "evt-123"},
            "periods": [],
        })
    )

    request = CreateSmartMeetingRequest(
        title="Weekly Sync",
        event_type=SmartSeriesEventType.TEAM_MEETING,
        ideal_time="10:00:00",
        duration_min_mins=30,
        defense_aggression=DefenseAggression.DEFAULT,
        organizer=Organizer(time_policy_type=TimePolicyType.WORK),
    )
    meeting = SmartMeeting.create(request)

    assert meeting.lineage_id == 9999999
    assert meeting.id == 9999999
    assert meeting.active_series is not None
    assert meeting.active_series.title == "Weekly Sync"


# ---------------------------------------------------------------------------
# Tests — patch / save
# ---------------------------------------------------------------------------


def test_save_uses_lineage_id_as_id(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.patch("/api/smart-meetings/4559766").mock(
        return_value=httpx.Response(200, json={
            "lineageId": 4559766,
            "type": "MEETING",
            "status": "ACTIVE",
            "enabled": True,
            "activeSeries": {"title": "Updated Title", "eventId": "evt-123"},
            "periods": [],
        })
    )

    meeting = SmartMeeting(
        lineage_id=4559766,
        id=4559766,
        type="MEETING",
        status="ACTIVE",
        enabled=True,
        active_series=SmartSeriesView(title="Old Title", event_id="evt-123"),
        periods=[],
    )
    meeting.save()

    assert meeting.active_series.title == "Updated Title"


def test_patch_request_serializes_correctly():
    request = PatchSmartMeetingRequest(title="New Title")
    data = request.model_dump(by_alias=True, exclude_none=True)
    assert data == {"title": "New Title"}


def test_patch_request_excludes_none_fields(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    route = mock_api.patch("/api/smart-meetings/4559766").mock(
        return_value=httpx.Response(200, json={
            "lineageId": 4559766,
            "type": "MEETING",
            "status": "ACTIVE",
            "enabled": True,
            "activeSeries": {"title": "Updated Title", "eventId": "evt-123"},
            "periods": [],
        })
    )

    meeting = SmartMeeting(
        lineage_id=4559766,
        id=4559766,
        type="MEETING",
        status="ACTIVE",
        enabled=True,
        periods=[],
    )
    meeting.save()

    # Verify the request body sent PATCH (not POST)
    assert route.called
    assert route.calls.last.request.method == "PATCH"


# ---------------------------------------------------------------------------
# Tests — update
# ---------------------------------------------------------------------------


def test_update_sends_patch_with_request_body(client, mock_api):
    route = mock_api.patch("/api/smart-meetings/4559766").mock(
        return_value=httpx.Response(200, json={
            "lineageId": 4559766,
            "type": "MEETING",
            "status": "ACTIVE",
            "enabled": True,
            "activeSeries": {"title": "Biweekly Sync", "eventId": "evt-123"},
            "periods": [],
        })
    )

    meeting = SmartMeeting(
        lineage_id=4559766,
        id=4559766,
        type="MEETING",
        status="ACTIVE",
        enabled=True,
        active_series=SmartSeriesView(title="Weekly Sync", event_id="evt-123"),
        periods=[],
    )
    result = meeting.update(PatchSmartMeetingRequest(title="Biweekly Sync"))

    assert route.called
    sent = json.loads(route.calls.last.request.content)
    assert sent == {"title": "Biweekly Sync"}
    # response is applied back onto the instance and returned
    assert result is meeting
    assert meeting.active_series.title == "Biweekly Sync"


def test_update_without_id_raises(client):
    meeting = SmartMeeting(type="MEETING", status="ACTIVE", enabled=True)
    with pytest.raises(ValueError, match="lineageId"):
        meeting.update(PatchSmartMeetingRequest(title="X"))


# ---------------------------------------------------------------------------
# Tests — delete
# ---------------------------------------------------------------------------


def test_delete_uses_lineage_id(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    route = mock_api.delete("/api/smart-meetings/4559766").mock(
        return_value=httpx.Response(200, json={})
    )

    meeting = SmartMeeting(
        lineage_id=4559766,
        id=4559766,
        type="MEETING",
        status="ACTIVE",
        enabled=True,
        active_series=SmartSeriesView(event_id="evt-123"),
        periods=[],
    )
    meeting.delete()
    assert route.called


# ---------------------------------------------------------------------------
# Tests — from_api_data
# ---------------------------------------------------------------------------


def test_from_api_data_sets_id_from_lineage_id(client):
    meeting = SmartMeeting.from_api_data(SAMPLE_RESPONSE)
    assert meeting.id == 4559766
    assert meeting.lineage_id == 4559766


def test_from_api_data_handles_missing_lineage_id(client):
    data = {"type": "MEETING", "status": "ACTIVE", "enabled": True}
    meeting = SmartMeeting.from_api_data(data)
    assert meeting.id is None
    assert meeting.lineage_id is None


# ---------------------------------------------------------------------------
# Tests — to_api_data
# ---------------------------------------------------------------------------


def test_to_api_data_excludes_lineage_id(client):
    meeting = SmartMeeting.from_api_data(SAMPLE_RESPONSE)
    data = meeting.to_api_data()
    assert "lineage_id" not in data
    assert "lineageId" not in data


# ---------------------------------------------------------------------------
# Tests — planner actions
# ---------------------------------------------------------------------------


def test_lock_requires_event_id(client, mock_api):
    """lock() should raise if activeSeries.eventId is missing."""
    meeting = SmartMeeting(
        lineage_id=4559766,
        type="MEETING",
        status="ACTIVE",
        enabled=True,
        active_series=SmartSeriesView(title="No Event ID"),
        periods=[],
    )
    with pytest.raises(ValueError, match="no eventId found"):
        meeting.lock()


def test_lock_sends_correct_request(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.post(
        "/api/smart-meetings/planner/reclaim0meeting0o030o045597660o04742904/lock"
    ).mock(
        return_value=httpx.Response(200, json={
            "events": [],
            "series": {"title": "Weekly Sync"},
            "userInfoMessage": "Locking series event",
            "timeoutReached": False,
        })
    )

    meeting = SmartMeeting.from_api_data(SAMPLE_RESPONSE)
    result = meeting.lock()

    assert result.user_info_message == "Locking series event"
    assert result.timeout_reached is False
    assert result.series is not None
    assert result.series.title == "Weekly Sync"


def test_unlock_sends_correct_request(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.post(
        "/api/smart-meetings/planner/reclaim0meeting0o030o045597660o04742904/unlock"
    ).mock(
        return_value=httpx.Response(200, json={
            "events": [],
            "series": {"title": "Weekly Sync"},
            "userInfoMessage": "Unlocking series event",
            "timeoutReached": False,
        })
    )

    meeting = SmartMeeting.from_api_data(SAMPLE_RESPONSE)
    result = meeting.unlock()
    assert result.user_info_message == "Unlocking series event"


def test_skip_sends_correct_request(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.post(
        "/api/smart-meetings/planner/reclaim0meeting0o030o045597660o04742904/skip"
    ).mock(
        return_value=httpx.Response(200, json={
            "events": [],
            "series": {"title": "Weekly Sync"},
            "userInfoMessage": "Skipped series event",
            "timeoutReached": False,
        })
    )

    meeting = SmartMeeting.from_api_data(SAMPLE_RESPONSE)
    result = meeting.skip()
    assert result.user_info_message == "Skipped series event"


def test_reschedule_sends_correct_request(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.post(
        "/api/smart-meetings/planner/reclaim0meeting0o030o045597660o04742904/reschedule"
    ).mock(
        return_value=httpx.Response(200, json={
            "events": [],
            "series": {"title": "Weekly Sync"},
            "userInfoMessage": "Rescheduled",
            "timeoutReached": False,
        })
    )

    meeting = SmartMeeting.from_api_data(SAMPLE_RESPONSE)
    result = meeting.reschedule("TOMORROW")
    assert result.user_info_message == "Rescheduled"


def test_move_sends_correct_request(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.post(
        "/api/smart-meetings/planner/reclaim0meeting0o030o045597660o04742904/move"
    ).mock(
        return_value=httpx.Response(200, json={
            "events": [],
            "series": {"title": "Weekly Sync"},
            "userInfoMessage": "Moved",
            "timeoutReached": False,
        })
    )

    meeting = SmartMeeting.from_api_data(SAMPLE_RESPONSE)
    start = datetime(2026, 6, 16, 10, 0, tzinfo=timezone.utc)
    end = datetime(2026, 6, 16, 10, 30, tzinfo=timezone.utc)
    result = meeting.move(start, end)
    assert result.user_info_message == "Moved"


def test_clear_exceptions_uses_lineage_id(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.post("/api/smart-meetings/planner/4559766/clear-exceptions").mock(
        return_value=httpx.Response(200, json={
            "events": [],
            "series": {"title": "Weekly Sync"},
            "userInfoMessage": "Reset schedule for Smart Series",
            "timeoutReached": False,
        })
    )

    meeting = SmartMeeting.from_api_data(SAMPLE_RESPONSE)
    result = meeting.clear_exceptions()
    assert result.user_info_message == "Reset schedule for Smart Series"


# ---------------------------------------------------------------------------
# Tests — class methods
# ---------------------------------------------------------------------------


def test_detect_calls_correct_endpoint(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.get("/api/smart-meetings/detect").mock(
        return_value=httpx.Response(200, json=[
            {"lineageId": 1, "type": "MEETING", "status": "ACTIVE", "enabled": True},
        ])
    )

    meetings = SmartMeeting.detect()
    assert len(meetings) == 1
    assert meetings[0].lineage_id == 1


def test_find_attendee_declined_calls_correct_endpoint(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.get("/api/smart-meetings/attendeeDeclined").mock(
        return_value=httpx.Response(200, json=[
            {"lineageId": 2, "type": "MEETING", "status": "ACTIVE", "enabled": True},
        ])
    )

    meetings = SmartMeeting.find_attendee_declined()
    assert len(meetings) == 1
    assert meetings[0].lineage_id == 2


def test_invite_organizer_calls_correct_endpoint(client, mock_api):
    mock_api.get("/api/users/current").mock(
        return_value=httpx.Response(200, json={"id": 1})
    )
    mock_api.post("/api/smart-meetings/invite-organizer").mock(
        return_value=httpx.Response(200, json={"status": "sent"})
    )

    result = SmartMeeting.invite_organizer([1, 2, 3])
    assert result["status"] == "sent"
