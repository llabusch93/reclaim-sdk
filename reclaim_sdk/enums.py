from enum import Enum


class PriorityLevel(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class EventCategory(str, Enum):
    WORK = "WORK"
    PERSONAL = "PERSONAL"
    BOTH = "BOTH"


class EventColor(str, Enum):
    NONE = "NONE"
    LAVENDER = "LAVENDER"
    SAGE = "SAGE"
    GRAPE = "GRAPE"
    FLAMINGO = "FLAMINGO"
    BANANA = "BANANA"
    TANGERINE = "TANGERINE"
    PEACOCK = "PEACOCK"
    GRAPHITE = "GRAPHITE"
    BLUEBERRY = "BLUEBERRY"
    BASIL = "BASIL"
    TOMATO = "TOMATO"


class TaskStatus(str, Enum):
    NEW = "NEW"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"


class TaskSource(str, Enum):
    """Task origin.

    Note: the plan pins ``TaskSource.RECLAIM = "RECLAIM"`` (see Task 6 test
    ``test_task_has_new_required_fields``).  Reclaim's own Swagger spec uses a
    schema called ``TaskSourceType`` with values like ``RECLAIM_APP``,
    ``CLICK_UP`` etc.  The ``taskSource`` field on ``Task`` in the Swagger is
    actually an object (the ``TaskSource`` schema) that *contains* a
    ``TaskSourceType`` enum — the SDK models it as a flat string enum with the
    commonly-used values to stay ergonomic.  If future tasks need the full
    object semantics, this enum can be widened without breaking consumers.
    """

    RECLAIM = "RECLAIM"
    GOOGLE = "GOOGLE"
    ASANA = "ASANA"
    CLICKUP = "CLICKUP"
    JIRA = "JIRA"
    TODOIST = "TODOIST"
    LINEAR = "LINEAR"


class SnoozeOption(str, Enum):
    """Snooze options — values match Reclaim Swagger ``SnoozeOption`` schema."""

    FROM_NOW_15M = "FROM_NOW_15M"
    FROM_NOW_30M = "FROM_NOW_30M"
    FROM_NOW_1H = "FROM_NOW_1H"
    FROM_NOW_2H = "FROM_NOW_2H"
    FROM_NOW_4H = "FROM_NOW_4H"
    TOMORROW = "TOMORROW"
    IN_TWO_DAYS = "IN_TWO_DAYS"
    NEXT_WEEK = "NEXT_WEEK"


class Weekday(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


class TimeSchemeFeature(str, Enum):
    """Capability flags a time scheme can serve.

    Values match the ``features`` array on ``/api/timeschemes`` payloads.
    """

    TASK_ASSIGNMENT = "TASK_ASSIGNMENT"
    HABIT_ASSIGNMENT = "HABIT_ASSIGNMENT"
    SMART_HABIT = "SMART_HABIT"
    ONE_ON_ONE_ASSIGNMENT = "ONE_ON_ONE_ASSIGNMENT"
    SMART_MEETING = "SMART_MEETING"
    SCHEDULING_LINK_MEETING = "SCHEDULING_LINK_MEETING"


class PolicyType(str, Enum):
    """Time-scheme policy type. ``CUSTOM`` is required to send a custom
    ``policy.dayHours`` payload; the others are server-managed presets that
    map to the user's main Work/Personal/Meeting hours."""

    CUSTOM = "CUSTOM"
    WORK = "WORK"
    PERSONAL = "PERSONAL"
    MEETING = "MEETING"


class EventSubType(str, Enum):
    """Event subtype — values match Reclaim Swagger ``EventSubType`` schema."""

    ONE_ON_ONE = "ONE_ON_ONE"
    STAFF_MEETING = "STAFF_MEETING"
    OP_REVIEW = "OP_REVIEW"
    EXTERNAL = "EXTERNAL"
    IDEATION = "IDEATION"
    FOCUS = "FOCUS"
    PRODUCTIVITY = "PRODUCTIVITY"
    TRAVEL = "TRAVEL"
    FLIGHT = "FLIGHT"
    TRAIN = "TRAIN"
    RECLAIM = "RECLAIM"
    VACATION = "VACATION"
    HEALTH = "HEALTH"
    ERRAND = "ERRAND"
    OTHER_PERSONAL = "OTHER_PERSONAL"
    UNKNOWN = "UNKNOWN"


class SmartSeriesEventType(str, Enum):
    """Event type for smart meeting series.

    Values match the Reclaim Swagger ``SmartSeriesEventType`` schema.
    """

    PERSONAL = "PERSONAL"
    SOLO_WORK = "SOLO_WORK"
    EXTERNAL_MEETING = "EXTERNAL_MEETING"
    FOCUS = "FOCUS"
    TEAM_MEETING = "TEAM_MEETING"
    ONE_ON_ONE = "ONE_ON_ONE"


class DefenseAggression(str, Enum):
    """How aggressively Reclaim defends smart-meeting time blocks.

    Values match the Reclaim Swagger ``DefenseAggression`` schema.
    """

    NONE = "NONE"
    LOW = "LOW"
    DEFAULT = "DEFAULT"
    HIGH = "HIGH"
    MAX = "MAX"


class SmartSeriesVisibility(str, Enum):
    """Visibility setting for smart-meeting series.

    Values match the Reclaim Swagger ``SmartSeriesVisibility`` schema.
    """

    DEFAULT = "DEFAULT"
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class ConferenceType(str, Enum):
    """Video conference provider for smart meetings.

    Values match the Reclaim Swagger ``ConferenceType`` schema.
    """

    ZOOM = "ZOOM"
    GOOGLE_MEET = "GOOGLE_MEET"
    MICROSOFT_TEAMS = "MICROSOFT_TEAMS"
    WEBEX = "WEBEX"
    FACETIME = "FACETIME"
    OTHER = "OTHER"


class SmartSeriesDependencyType(str, Enum):
    """Dependency type for smart-meeting series.

    Values match the Reclaim Swagger ``SmartSeriesDependencyType`` schema.
    """

    NONE = "NONE"
    TASK = "TASK"
    HABIT = "HABIT"


class SmartSeriesBookingFailurePolicy(str, Enum):
    """What Reclaim does when it cannot book a smart-meeting instance.

    Values match the Reclaim Swagger ``SmartSeriesBookingFailurePolicy`` schema.
    """

    LEAVE_LAST_OR_RETURN_TO_ORIGINAL = "LEAVE_LAST_OR_RETURN_TO_ORIGINAL"
    LEAVE_LAST = "LEAVE_LAST"
    RETURN_TO_ORIGINAL = "RETURN_TO_ORIGINAL"


class SmartSeriesAttendeeResponseStatus(str, Enum):
    """Attendee response status for smart meetings.

    Values match the Reclaim Swagger ``SmartSeriesAttendeeResponseStatus`` schema.
    """

    NEEDS_ACTION = "NEEDS_ACTION"
    ACCEPTED = "ACCEPTED"
    TENTATIVE = "TENTATIVE"
    DECLINED = "DECLINED"


class SmartSeriesStatus(str, Enum):
    """Lifecycle status of a smart-meeting series.

    Values match the Reclaim Swagger ``SmartSeriesStatus`` schema.
    """

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


class SmartSeriesRecurrenceType(str, Enum):
    """Recurrence type for a smart-meeting series.

    Values match the Reclaim Swagger ``SmartSeriesRecurrenceType`` schema.
    """

    RECURRING_SERIES = "RECURRING_SERIES"
    SINGLE_INSTANCE = "SINGLE_INSTANCE"


class Frequency(str, Enum):
    """Recurrence frequency.

    Values match the Reclaim Swagger ``Frequency`` schema.
    """

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class TimePolicyType(str, Enum):
    """Time-policy type for organizers/attendees.

    Values match the Reclaim Swagger ``TimePolicyType`` schema.
    """

    WORK = "WORK"
    PERSONAL = "PERSONAL"
    MEETING = "MEETING"
