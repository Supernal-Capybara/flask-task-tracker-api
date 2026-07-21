# Task Tracker API (Flask + SQLite)

A simple REST-style API for managing tasks using Flask and SQLite.
This project demonstrates building a small CRUD-style backend service suitable for internal tools or lightweight applications.

## Features
* Create tasks
* Retrieve all tasks or filter via query parameters
* Retrieve a task by ID
* Update tasks (PATCH)
* Delete tasks
* Query filtering via URL parameters
* Pytest test suite 

## Technologies Used
* Python
* Flask
* SQLite
* Requests (for API testing)
* Pytest

## How to Run
* Start the Flask server: `task_tracker.py`
* The API will be available at: http://127.0.0.1:5000/
* Example usage:
    * Get all tasks: http://127.0.0.1:5000/tasks
    * Filter tasks: `http://127.0.0.1:5000/tasks?task_name=replicant maintenance`
    * Get tasks by ID: http://127.0.0.1:5000/tasks/1

## API Endpoints
| Method | Endpoint     | Description                      |
| ------ | -------------| -------------------------------- |
| GET    | /tasks       | Get all tasks (supports filters) |
| GET    | /tasks/{id}  | Get a single task                |
| POST   | /tasks       | Create a new task                |
| PATCH  | /tasks/{id}  | Update a task                    |
| DELETE | /tasks/{id}  | Delete a task                    |


## Requirements
* Python installed
* Requests library installed
* Flask library installed
* Pytest framework installed
* Install dependencies: 
    * pip install -r requirements.txt

## Skills Demonstrated
* Building REST-style APIs with Flask
* SQLite database integration
* CRUD operations
* Query parameter filtering
* JSON request/response handling
* Dynamic SQL query construction for filtering and updates
* API testing with pytest and Flask’s test client
* Test isolation using temporary SQLite databases

## Notes
* This project runs locally using Flask’s development server
* The included `api_client.py` file demonstrates how to interact with the API using the `requests` library
* The SQLite database file is created automatically when the application runs
* Ensure all files are saved in the same folder

## Testing
* The pytest suite uses Flask’s test client and an isolated temporary SQLite database to test API responses, validation, filtering, CRUD operations, and database persistence
* Run the test suite in PowerShell: `py -m pytest -v`    

## Upcoming features
* Build a simple CLI or frontend interface
* Make validation case-insensitive 