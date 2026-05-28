import os
import uuid
import pytest
from reclaim_sdk.client import ReclaimClient


SDK_LIVE_PREFIX = f"[sdk-test-{uuid.uuid4().hex[:8]}]"


@pytest.fixture(scope="session")
def live_client():
    token = os.environ.get("RECLAIM_TOKEN")
    if not token:
        pytest.skip("RECLAIM_TOKEN not set")
    return ReclaimClient.configure(token=token)


@pytest.fixture(scope="session")
def tracked_ids():
    """Registry of resources created during the session. Cleaned up in finalizer."""
    registry = {"tasks": [], "habits": [], "webhooks": [], "smart_meetings": []}
    yield registry

    from reclaim_sdk.resources.task import Task
    from reclaim_sdk.resources.habit import DailyHabit
    from reclaim_sdk.resources.webhook import Webhook
    from reclaim_sdk.resources.smart_meeting import SmartMeeting

    errors = []
    for task_id in registry["tasks"]:
        try:
            t = Task.get(task_id)
            t.delete()
        except Exception as e:
            errors.append(f"task {task_id}: {e}")
    for habit_id in registry["habits"]:
        try:
            h = DailyHabit.get(habit_id)
            h.delete()
        except Exception as e:
            errors.append(f"habit {habit_id}: {e}")
    for wh_id in registry["webhooks"]:
        try:
            w = Webhook.get(wh_id)
            w.delete()
        except Exception as e:
            errors.append(f"webhook {wh_id}: {e}")
    for sm_id in registry["smart_meetings"]:
        try:
            SmartMeeting.get(sm_id).delete()
        except Exception as e:
            errors.append(f"smart_meeting {sm_id}: {e}")

    # paranoid sweep
    try:
        for t in Task.list():
            if t.title and t.title.startswith(SDK_LIVE_PREFIX):
                t.delete()
    except Exception as e:
        errors.append(f"task sweep: {e}")

    # sweep smart meetings by title prefix
    try:
        for sm in SmartMeeting.list():
            if sm.active_series and sm.active_series.title and sm.active_series.title.startswith(SDK_LIVE_PREFIX):
                sm.delete()
    except Exception as e:
        errors.append(f"smart_meeting sweep: {e}")

    if errors:
        raise RuntimeError("Live cleanup failures: " + "; ".join(errors))


@pytest.fixture
def prefix():
    return SDK_LIVE_PREFIX
