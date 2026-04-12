# Task Tracker API (Flask + SQLite)

A simple REST-style API for managing tasks using Flask and SQLite.
This project demonstrates building a small CRUD-style backend service suitable for internal tools or lightweight applications.

# Features
* Create tasks
* Retrieve all tasks or filter via query parameters
* Retrieve a task by ID
* Update tasks (PATCH)
* Delete tasks
* Query filtering via URL parameters

Technologies Used
* Python
* Flask
* SQLite
* Requests (for API testing)

How to Run
* Start the Flask server: `task_tracker.py`
* The API will be available at: http://127.0.0.1:5000/
* Example usage:
    * Get all tasks: http://127.0.0.1:5000/tasks
    * Filter tasks: http://127.0.0.1:5000/tasks?task_name=replicant maintenance
    * Get tasks by ID: http://127.0.0.1:5000/tasks/1

# API Endpoints
| Method | Endpoint     | Description                      |
| ------ | ------------ | -------------------------------- |
| GET    | /tasks       | Get all tasks (supports filters) |
| GET    | /tasks/<id>  | Get a single task                |
| POST   | /tasks       | Create a new task                |
| PATCH  | /tasks/<id>  | Update a task                    |
| DELETE | /tasks/<id>  | Delete a task                    |


Requirements
* Python installed
* Requests library installed
* Flask library installed
* Install dependencies: 
    * pip install -r requirements.txt

Skills Demonstrated
* Building REST-style APIs with Flask
* SQLite database integration
* CRUD operations
* Query parameter filtering
* JSON request/response handling
* Dynamic SQL query construction for filtering and updates

Notes
* This project runs locally using Flask’s development server
* The included `api_client.py` file demonstrates how to interact with the API using the `requests` library
* The SQLite database file is created automatically when the application runs

Upcoming features
* Add update PUT functionality
* Build a simple CLI or frontend interface
* Make validation case-insensitive 