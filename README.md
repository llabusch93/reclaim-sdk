# Reclaim-SDK - Unofficial Python SDK for Reclaim.ai

⚠️ **WARNING: Major Changes in Version 0.5+** ⚠️

The codebase has undergone significant changes from version 0.5 onwards. These changes introduce breaking changes that may affect existing implementations. Please review the documentation carefully when upgrading from earlier versions.

Reclaim-SDK is an unofficial Python SDK for the Reclaim.ai API. It provides a simple and easy-to-use interface for managing tasks in Reclaim.ai. Please note that this SDK is not affiliated with Reclaim.ai in any way and was reverse-engineered from the Reclaim.ai web app and [using the Swagger Spec](https://api.app.reclaim.ai/swagger/reclaim-api-0.1.yml), thanks to AJ from Reclaim.ai to provide that! As a result, there may be bugs and the API may change at any time, and versioning is not guaranteed to be stable.

## Features
Currently, Reclaim-SDK only supports task management. However, as there might be an official SDK in the future, this SDK won't implement all features of the web app. 

## Installation
To install Reclaim-SDK, simply run the following command:
```bash
pip install reclaim-sdk
```

## Configuration
You can get an API key from [here](https://app.reclaim.ai/settings/developer).

There are now two ways to configure the SDK with your API key:

1. Using the `RECLAIM_TOKEN` environment variable:
   ```python
   import os
   os.environ["RECLAIM_TOKEN"] = "YOUR_API_KEY"
   ```

2. Using the new `configure` method:
   ```python
   from reclaim_sdk.client import ReclaimClient
   
   ReclaimClient.configure(token="YOUR_API_KEY")
   ```

The `configure` method allows you to set up the client with your API token (and optionally a base URL) at any point in your code before making API calls.

## Usage
The SDK uses Pydantic models for better type checking and data validation. Here's an example of how to use the Task resource:

### Creating a task
```python
from reclaim_sdk.resources.task import Task
from datetime import datetime, timedelta

# Create a new task
task = Task(
    title="My new task",
    due=datetime.now() + timedelta(days=5),
    priority="P1"
)

# Set durations
task.duration = 5
task.min_work_duration = 0.75
task.max_work_duration = 2

# Save the task
task.save()
```

### Updating tasks
```python
# Update task properties
task.notes = "Updated description"
task.save()

# Add time to the task
task.add_time(0.5)  # Add 30 minutes

# Set the task to be in the up next list
task.up_next = True
task.save()
```

### Task operations
```python
# Start the task
task.start()

# Log work on the task
task.log_work(60, datetime.now())

# Stop the task
task.stop()

# Mark the task as complete
task.mark_complete()

# Mark the task as incomplete
task.mark_incomplete()
```

### Listing tasks
```python
# List all tasks
all_tasks = Task.list()
```

### Deleting tasks
```python
# Delete a task
task.delete()
```

## Error Handling
The SDK provides specific exceptions for better error handling:

```python
from reclaim_sdk.exceptions import RecordNotFound, InvalidRecord, AuthenticationError, ReclaimAPIError

try:
    # Your code here
except RecordNotFound as e:
    print(f"Record not found: {e}")
except InvalidRecord as e:
    print(f"Invalid record: {e}")
except AuthenticationError as e:
    print(f"Authentication error: {e}")
except ReclaimAPIError as e:
    print(f"API error: {e}")
```

## Contributing
Contributions are welcome. Please open an issue or a pull request. If you want to add a new resource, please have a look at the `BaseResource` class and the `Task` class. The `Task` class is a good example of how to implement a new resource.

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