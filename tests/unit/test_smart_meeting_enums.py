"""Tests for smart-meeting-related enums."""

from reclaim_sdk.enums import (
    SmartSeriesEventType,
    DefenseAggression,
    SmartSeriesVisibility,
    ConferenceType,
    SmartSeriesDependencyType,
    SmartSeriesBookingFailurePolicy,
    SmartSeriesAttendeeResponseStatus,
    SmartSeriesStatus,
    SmartSeriesRecurrenceType,
    Frequency,
    TimePolicyType,
)


def test_smart_series_event_type_values():
    values = {e.value for e in SmartSeriesEventType}
    assert values == {
        "PERSONAL", "SOLO_WORK", "EXTERNAL_MEETING",
        "FOCUS", "TEAM_MEETING", "ONE_ON_ONE",
    }


def test_smart_series_event_type_count():
    assert len(list(SmartSeriesEventType)) == 6


def test_defense_aggression_values():
    values = {e.value for e in DefenseAggression}
    assert values == {"NONE", "LOW", "DEFAULT", "HIGH", "MAX"}
    assert len(list(DefenseAggression)) == 5


def test_smart_series_visibility_values():
    values = {e.value for e in SmartSeriesVisibility}
    assert values == {"DEFAULT", "PRIVATE", "PUBLIC"}


def test_conference_type_values():
    values = {e.value for e in ConferenceType}
    assert "ZOOM" in values
    assert "GOOGLE_MEET" in values
    assert len(list(ConferenceType)) >= 5


def test_smart_series_dependency_type_values():
    values = {e.value for e in SmartSeriesDependencyType}
    assert values == {"NONE", "TASK", "HABIT"}


def test_smart_series_booking_failure_policy_values():
    values = {e.value for e in SmartSeriesBookingFailurePolicy}
    assert "LEAVE_LAST_OR_RETURN_TO_ORIGINAL" in values
    assert "LEAVE_LAST" in values
    assert "RETURN_TO_ORIGINAL" in values


def test_smart_series_attendee_response_status_values():
    values = {e.value for e in SmartSeriesAttendeeResponseStatus}
    assert values == {"NEEDS_ACTION", "ACCEPTED", "TENTATIVE", "DECLINED"}


def test_smart_series_status_values():
    values = {e.value for e in SmartSeriesStatus}
    assert values == {"ACTIVE", "DISABLED", "ARCHIVED"}


def test_smart_series_recurrence_type_values():
    values = {e.value for e in SmartSeriesRecurrenceType}
    assert values == {"RECURRING_SERIES", "SINGLE_INSTANCE"}


def test_frequency_values():
    values = {e.value for e in Frequency}
    assert values == {"DAILY", "WEEKLY", "MONTHLY"}


def test_time_policy_type_values():
    values = {e.value for e in TimePolicyType}
    assert values == {"WORK", "PERSONAL", "MEETING"}
