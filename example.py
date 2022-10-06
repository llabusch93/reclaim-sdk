from reclaimai_sdk.models.task import ReclaimTask

# Get the desired task
task = ReclaimTask.get(12345)

# Delete the task
task.delete()
