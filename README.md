# reclaim-sdk - Unofficial Reclaim.ai Python SDK

This is an unofficial Python SDK for the Reclaim.ai API. It is not affiliated with Reclaim.ai in any way and was reverse engineered from the Reclaim.ai web app.
That means there can be bugs and the API may change at any time, a versioning is not possible.

## Features
**Currently only task management is supported**. As there might be an official SDK in the future, this SDK won't implement all features of the web app.

## Installation

```bash
pip install reclaim-sdk
```

## Configuration
The only configuration needed is the token. You can get it from the Reclaim.ai web app, by copying it from the browser's developer tools. It's stored in the cookie named `RECLAIM`.

There are 3 ways to configure the token:

1. You can initiate the `ReclaimClient` class with the token as the `token` argument. As `ReclaimClient` is a singleton, you should initiate this class at the beginning of your script / program. It will be used for all subsequent calls.
2. You can set the environment variable `RECLAIM_TOKEN` to the token.
3. You can store the token in a toml file named `.reclaim.toml` in your home directory. It should look like this:

```toml
[reclaim_ai]
token = <YOUR_TOKEN>
```

## Usage
All CRUD operations are supported, but for now only tasks are implemented. For the linked task events only the update of start and end times are supported. Nevertheless the API is designed to be easily extendable, by adding new classes for other resources. All "heavy lifting" is done in the `ReclaimModel` class, which is the base class for all other models.

### Creating a task
```python
from reclaim_sdk.models.task import ReclaimTask
from datetime import datetime, timedelta

# The objects can be used as context managers, so they will automatically
# be saved to the API when exiting the context.
with ReclaimTask() as task:
    task.name = "test_task_12345"
    # All durations are set in hours
    task.duration = 5
    task.min_work_duration = 0.75
    task.max_work_duration = 2
    # The start date is set to 3 days in the future
    task.start_date = datetime.now() + timedelta(days=3)
    # The due date is set to 5 days in the future
    task.due_date = datetime.now() + timedelta(days=5)

# It is also possible to create an object without using a context manager.
task = ReclaimTask()

task.name = "test_task_12345"
task.duration = 5
task.min_work_duration = 0.75
task.max_work_duration = 2
task.start_date = datetime.now() + timedelta(days=3)
task.due_date = datetime.now() + timedelta(days=5)

# Then the object needs to be saved manually to the API.
task.save()
```

### Updating and searching tasks
```python
from reclaim_sdk.models.task import ReclaimTask

# By default the search method returns all tasks except archived ones
# (marked as completed)
tasks = ReclaimTask.search()

# Setting all tasks to work tasks
for task in tasks:
    with task:
        task.is_work_task = True

# We can also search for tasks by name or other fields
# (but they have to be exact matches)
tasks = ReclaimTask.search(title="My task")

# If we have the task ID we can get the task directly
task = ReclaimTask.get(12345)

```

### Deleting tasks
```python
from reclaim_sdk.models.task import ReclaimTask

# Get the desired task
task = ReclaimTask.get(12345)

# Delete the task
task.delete()
```

### Prioritizing tasks
```python
from reclaim_sdk.models.task import ReclaimTask

# Get the desired tasks
task = ReclaimTask.get(12345)

# Prioritize one task on top of all the other
task.prioritize()

# Prioritize the tasks by due date
# (Sorts the tasks by due date and sets the priorities accordingly)
ReclaimTask.prioritize_by_due()
```

### Change start and end date for task events
```python
from reclaim_sdk.models.task import ReclaimTask

# Get the desired task
task = ReclaimTask.get(12345)

# Adding one hour to the end date of the first event
# (so the event gets 1 hour longer)
with task.events[0] as event:
    event.end = event.end + timedelta(hours=1)
```

## Contributing
Contributions are welcome. Please open an issue or a pull request. If you want to add a new resource, please have a look at the `ReclaimModel` class and the `ReclaimTask` class. The `ReclaimTask` class is a good example of how to implement a new resource.

## License
[MIT License](https://choosealicense.com/licenses/mit/)

Copyright (c) 2022 Laurence Labusch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
