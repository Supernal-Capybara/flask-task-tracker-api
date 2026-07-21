
import task_tracker
from task_tracker import app, create_task
import pytest
import sqlite3

@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client
        
  
def test_sending_post_without_json_data(client):
    response = client.post("/tasks")
    
    data = response.get_json()
    
    assert response.status_code == 400
    assert data == {"error": "no data provided"}
    
@pytest.fixture
def test_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test_task_tracker.db"

    monkeypatch.setattr(task_tracker, "DATABASE", db_path)
    task_tracker.create_table(db_path)

    return db_path

@pytest.fixture
def client(test_db):
    task_tracker.app.config["TESTING"] = True

    with task_tracker.app.test_client() as client:
        yield client
        
        

def test_successful_post_request(client, test_db):
    new_task = {
        "task_name": "Update inventory",
        "priority": "urgent",
        "status": "not yet started",
        "assigned_to": "Maria"}

    response = client.post("/tasks", json=new_task)
    data = response.get_json()
    
    assert response.status_code == 201
    assert data["id"] > 0
    
    assert data["task_name"] == new_task["task_name"]
    assert data["priority"] == new_task["priority"]
    assert data["status"] == new_task["status"]
    assert data["assigned_to"] == new_task["assigned_to"]
    
    
    with sqlite3.connect(test_db) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, task_name, priority, status, assigned_to
            FROM task_tracker
            WHERE id = ?
            """,
            (data["id"],)
        )
        row = cur.fetchone()


    assert row is not None
    assert row["task_name"] == new_task["task_name"]
    assert row["priority"] == new_task["priority"]
    assert row["status"] == new_task["status"]
    assert row["assigned_to"] == new_task["assigned_to"]
    



def test_get_task_by_id(client):
    new_task = {
        "task_name": "Update inventory",
        "priority": "urgent",
        "status": "not yet started",
        "assigned_to": "Maria",
    }

    create_response = client.post("/tasks", json=new_task)
    created_data = create_response.get_json()

    assert create_response.status_code == 201

    task_id = created_data["id"]

    get_response = client.get(f"/tasks/{task_id}")
    returned_data = get_response.get_json()

    assert get_response.status_code == 200
    assert returned_data == created_data



def test_get_task_by_id_not_found(client):

    response = client.get("/tasks/9999")
    data = response.get_json()
    
    assert response.status_code == 404
    assert data == {"error": "task not found"}
    


  

def test_get_all_tasks(client):
    task_one = {
        "task_name": "Update inventory",
        "priority": "urgent",
        "status": "not yet started",
        "assigned_to": "Maria",
    }
    
    task_two = {
        "task_name": "Fix rocket engines",
        "priority": "urgent",
        "status": "completed",
        "assigned_to": "Emily",
    }
    
    response_one = client.post("/tasks", json=task_one)
    response_two = client.post("/tasks", json=task_two)
    
    
    assert response_one.status_code == 201
    assert response_two.status_code == 201

    
    get_response = client.get("/tasks")
    
    assert get_response.status_code == 200
    
    data = get_response.get_json()
    
    
    assert isinstance(data, list)
    assert len(data) == 2
    
    
    task_names = [task["task_name"] for task in data]
    
    
    assert set(task_names) == {"Update inventory", "Fix rocket engines"}


        
def test_query_parameter_filtering(client):
    
    task_one = {
        "task_name": "Update inventory",
        "priority": "urgent",
        "status": "not yet started",
        "assigned_to": "Maria",
    }
    
    task_two = {
        "task_name": "Fix rocket engines",
        "priority": "routine",
        "status": "completed",
        "assigned_to": "Emily",
    }
    
    client.post("/tasks", json=task_one)
    client.post("/tasks", json=task_two)

    
    response_one = client.get(
    "/tasks",
    query_string={"priority": "urgent"},
)

    assert response_one.status_code == 200
   
    data = response_one.get_json()
    
    assert isinstance(data, list)
    assert len(data) == 1
    
    assert data[0]["priority"] == "urgent"
    assert data[0]["task_name"] == task_one["task_name"]
    



def test_patch(client):
    task_one = {
        "task_name": "Update inventory",
        "priority": "urgent",
        "status": "not yet started",
        "assigned_to": "Maria",
    }
    
    response = client.post("/tasks", json=task_one)
    
    assert response.status_code == 201
    
    data = response.get_json()
    
    task_id = data["id"]
    
    task_one_update = {
        "task_name": "Update inventory",
        "priority": "urgent",
        "status": "completed",
        "assigned_to": "Maria",
    }
    
    response_two = client.patch(f"/tasks/{task_id}", json=task_one_update)
    
    data_two = response_two.get_json()
    
    assert response_two.status_code == 200
    assert data_two["status"] == "completed"
    
    
    response_three = client.get(f"/tasks/{task_id}")
    data_three = response_three.get_json()
    
    assert response_three.status_code == 200
    assert data_three["status"] == "completed"
    
    

    
def test_delete_task(client):
    task_one = {
        "task_name": "Update inventory",
        "priority": "urgent",
        "status": "not yet started",
        "assigned_to": "Maria",
    }
    
    response = client.post("/tasks", json=task_one)
    assert response.status_code == 201
    
    data = response.get_json()
    
    task_id = data["id"]
    
    
    response_two = client.delete(f"/tasks/{task_id}")
    
    data_two = response_two.get_json()
    
    assert response_two.status_code == 200
    assert data_two == {"message": f"task {task_id} deleted successfully"}
 
    response_three = client.get(f"/tasks/{task_id}")
    data_three = response_three.get_json()
    
    
    assert response_three.status_code == 404
    assert data_three == {"error": "task not found"}
        
        
        

def test_post_rejects_invalid_priority(client):
    task = {
        "task_name": "Update inventory",
        "priority": "extremely important",
        "status": "not yet started",
        "assigned_to": "Maria",
    }
    
    response = client.post("/tasks", json=task)
    
    assert response.status_code == 400
    
    data = response.get_json()
    
    assert data == {"error": "priority must be either 'routine' or 'urgent'"}

    
    
