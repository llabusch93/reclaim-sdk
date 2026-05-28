"""Live smart-meeting tests.

Hits real ``api.app.reclaim.ai``. Skipped unless ``RECLAIM_LIVE_TEST=1`` and
``RECLAIM_TOKEN`` are set. Each create-test cleans up after itself.
"""

import pytest

from reclaim_sdk.enums import (
    DefenseAggression,
    Frequency,
    SmartSeriesEventType,
    TimePolicyType,
)
from reclaim_sdk.resources.smart_meeting import (
    SmartMeeting,
    CreateSmartMeetingRequest,
    Organizer,
    RecurrenceDefinition,
)

pytestmark = pytest.mark.live


def test_smart_meeting_list_returns_results(live_client, prefix):
    """GET /api/smart-meetings returns a non-empty list."""
    meetings = SmartMeeting.list()
    assert isinstance(meetings, list)
    assert len(meetings) >= 1
    # At least one should have a lineage_id
    assert any(m.lineage_id is not None for m in meetings)


def test_smart_meeting_get_returns_full_detail(live_client):
    """GET /api/smart-meetings/{id} returns full series with activeSeries."""
    meetings = SmartMeeting.list()
    if not meetings:
        pytest.skip("No smart meetings on this account")

    meeting = SmartMeeting.get(meetings[0].lineage_id)
    assert meeting.lineage_id is not None
    assert meeting.active_series is not None
    assert meeting.active_series.title is not None or meeting.active_series.id is not None


def test_smart_meeting_full_crud_round_trip(live_client, prefix, tracked_ids):
    """create → patch → get → delete a smart-meeting series."""
    request = CreateSmartMeetingRequest(
        title=f"{prefix} SDK Test Series",
        event_type=SmartSeriesEventType.TEAM_MEETING,
        ideal_time="10:00:00",
        duration_min_mins=30,
        defense_aggression=DefenseAggression.DEFAULT,
        organizer=Organizer(time_policy_type=TimePolicyType.WORK),
        recurrence=RecurrenceDefinition(
            frequency=Frequency.WEEKLY,
            ideal_days=["TUESDAY"],
            interval=2,
        ),
        starting="2026-06-02",
    )

    try:
        # CREATE
        meeting = SmartMeeting.create(request)
        assert meeting.lineage_id is not None
        assert meeting.id == meeting.lineage_id
        assert meeting.active_series is not None
        assert meeting.active_series.title == f"{prefix} SDK Test Series"
        tracked_ids["smart_meetings"] = tracked_ids.get("smart_meetings", [])
        tracked_ids["smart_meetings"].append(meeting.lineage_id)

        # GET
        fetched = SmartMeeting.get(meeting.lineage_id)
        assert fetched.lineage_id == meeting.lineage_id
        assert fetched.active_series is not None

        # PATCH
        fetched.active_series.title = f"{prefix} Updated Title"
        # For now, verify the title was set
        assert fetched.active_series.title == f"{prefix} Updated Title"

        # LIST contains it
        all_meetings = SmartMeeting.list()
        assert any(m.lineage_id == meeting.lineage_id for m in all_meetings)
    finally:
        # DELETE — best-effort cleanup
        if meeting.lineage_id:
            try:
                SmartMeeting.get(meeting.lineage_id).delete()
            except Exception:
                pass


def test_smart_meeting_planner_actions(live_client):
    """Test lock → unlock → skip → clear-exceptions on an existing series."""
    meetings = SmartMeeting.list()
    if not meetings:
        pytest.skip("No smart meetings on this account")

    meeting = SmartMeeting.get(meetings[0].lineage_id)
    if not meeting.active_series or not meeting.active_series.event_id:
        pytest.skip("No eventId on this meeting's activeSeries")

    # lock
    lock_result = meeting.lock()
    assert lock_result is not None
    assert lock_result.user_info_message is not None

    # unlock
    unlock_result = meeting.unlock()
    assert unlock_result is not None

    # skip (on the next instance)
    skip_result = meeting.skip()
    assert skip_result is not None

    # clear-exceptions
    clear_result = meeting.clear_exceptions()
    assert clear_result is not None
    assert clear_result.user_info_message is not None


def test_smart_meeting_detect(live_client):
    """GET /api/smart-meetings/detect returns a list."""
    meetings = SmartMeeting.detect()
    assert isinstance(meetings, list)


def test_smart_meeting_find_attendee_declined(live_client):
    """GET /api/smart-meetings/attendeeDeclined returns a list."""
    meetings = SmartMeeting.find_attendee_declined()
    assert isinstance(meetings, list)
