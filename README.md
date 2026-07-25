# Task Tracker API (Flask + PostgreSQL)
A REST-style API for managing tasks with Flask and PostgreSQL. The project began with SQLite and was migrated to PostgreSQL while preserving the existing HTTP endpoints and JSON interface.

## Features
* Create tasks
* Retrieve all tasks or filter them with query parameters
* Retrieve a task by ID
* Partially update tasks with PATCH
* Delete tasks
* Validate task data in Flask and with PostgreSQL constraints
* Test API behavior and database persistence with pytest

## Technologies Used
* Python
* Flask
* PostgreSQL
* Psycopg 3
* Requests
* pytest


## API Endpoints
| Method | Endpoint      | Description                      |
|--------|---------------|----------------------------------|
| GET    | `/tasks`      | Get all tasks (supports filters) |
| GET    | `/tasks/{id}` | Get a single task                |
| POST   | `/tasks`      | Create a new task                |
| PATCH  | `/tasks/{id}` | Update a task                    |
| DELETE | `/tasks/{id}` | Delete a task                    |
Supported filters for GET /tasks are id, task_name, priority, status, and assigned_to.

## Local Setup
1. Create and activate a virtual environment
In PowerShell:
`py -m venv .venv`
`.venv\Scripts\Activate.ps1`

Install the dependencies:
`python -m pip install -r requirements.txt`

2. Create the PostgreSQL databases
The application connects with a PostgreSQL role named `task_app`. Create the development and test databases with that role as their owner:

```sql
CREATE DATABASE task_tracker_db
OWNER task_app;
```

```sql
CREATE DATABASE task_tracker_test_db
OWNER task_app;
```

The `task_tracker` table is created automatically when the application or test suite runs.

3. Set the database password
Store the password for `task_app` in an environment variable rather than in the source code:
`$env:POSTGRES_PASSWORD = "your-password"`

This variable lasts for the current PowerShell session and must be set again after opening a new session.

The application uses `task_tracker_db` by default. To select a different database, set the optional `POSTGRES_DB` variable:
`$env:POSTGRES_DB = "database-name"`

Do not set `POSTGRES_DB` to `task_tracker_test_db` when running the development server because pytest clears the test table between tests.

4. Run the application
`python task_tracker.py`

The API will be available at http://127.0.0.1:5000.

Example requests:
http://127.0.0.1:5000/tasks
http://127.0.0.1:5000/tasks?priority=urgent
http://127.0.0.1:5000/tasks/1

The included `api_client.py` demonstrates POST, GET, PATCH, and DELETE requests with the Requests library.

## Testing
Run the test suite from the project directory:
`python -m pytest -v`

The tests use Flask's test client and the dedicated `task_tracker_test_db` PostgreSQL database. The table is truncated and its identity sequence is reset before and after each test, keeping tests isolated from one another and from development data.

The suite covers:
* Request validation
* Creating tasks and verifying database persistence
* Retrieving individual tasks
* Retrieving and filtering multiple tasks
* Updating tasks
* Deleting tasks
* Successful responses and expected error responses

## Skills Demonstrated
* Building REST-style APIs with Flask
* Migrating an application from SQLite to PostgreSQL
* PostgreSQL integration with Psycopg 3
* CRUD operations and parameterized SQL
* Dynamic SQL construction for filtering and partial updates
* PostgreSQL identity columns, CHECK constraints, and RETURNING
* Environment-based database configuration
* JSON request and response handling
* API testing with pytest and Flask's test client
* Test isolation with a dedicated PostgreSQL database

## Notes
* This project runs locally with Flask's development server
* The API's endpoints and JSON interface were preserved during the   SQLite-to-PostgreSQL migration
* The application accepts routine or urgent for priority
* The application accepts not yet started, ongoing, or completed for status
