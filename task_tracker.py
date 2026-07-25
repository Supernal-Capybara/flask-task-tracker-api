
from flask import Flask, jsonify, request
from pathlib import Path
import os
import psycopg
from psycopg.rows import dict_row


app = Flask(__name__)

def get_db_connection():
    password = os.environ.get("POSTGRES_PASSWORD")

    if password is None:
        raise RuntimeError(
            "POSTGRES_PASSWORD environment variable is not set"
        )

    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname=os.environ.get("POSTGRES_DB", "task_tracker_db"),
        user="task_app",
        password=password,
        row_factory=dict_row
    )


def create_table():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS task_tracker (
                        id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        task_name TEXT NOT NULL,
                        priority TEXT NOT NULL
                            CHECK (priority IN ('routine', 'urgent')),
                        status TEXT NOT NULL
                            CHECK (
                                status IN (
                                    'not yet started',
                                    'ongoing',
                                    'completed'
                                )
                            ),
                        assigned_to TEXT NOT NULL
                    );
                    """
                )

    except psycopg.Error as error:
        print(f"Database error: {error}")



@app.route("/tasks", methods=["POST"])
def create_task():
    valid_statuses = {"not yet started", "ongoing", "completed"}
    valid_priorities = {"routine", "urgent"}
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "no data provided"}), 400
    
    task_name = data.get("task_name")
    if task_name:
        task_name = task_name.strip()
        
    priority = data.get("priority")
    if priority:
        priority = priority.strip()
        if priority not in valid_priorities:
            return jsonify({"error": "priority must be either 'routine' or 'urgent'"}), 400
        
    status = data.get("status")
    if status:
        status = status.strip()
        if status not in valid_statuses:
            return jsonify({"error": "status must be 'not yet started', 'ongoing' or 'completed'"}), 400
        
    assigned_to = data.get("assigned_to")
    if assigned_to:
        assigned_to = assigned_to.strip()
        
    if not task_name or not priority or not status or not assigned_to:
        return jsonify({"error": "task_name, priority, status, and assigned_to must all be present"}), 400
    
    
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO task_tracker (
                        task_name,
                        priority,
                        status,
                        assigned_to
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, task_name, priority, status, assigned_to;
                    """,
                    (task_name, priority, status, assigned_to)
                )
                
                new_task = cursor.fetchone()

                return jsonify(new_task), 201
                
    except psycopg.Error:
        return jsonify({"error": "database error"}), 500



@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    
    task_id = request.args.get("id")
    if task_id:
        task_id = task_id.strip()
        if not task_id.isdigit():
            return jsonify({"error": "id must be an integer"}), 400
    
    task_name = request.args.get("task_name")
    if task_name:
        task_name = task_name.strip()
    
    priority = request.args.get("priority")
    if priority:
        priority = priority.strip()
        
    status = request.args.get("status")
    if status:
        status = status.strip()
        
    assigned_to = request.args.get("assigned_to")
    if assigned_to:
        assigned_to = assigned_to.strip()
    
    
    query = """
    SELECT id, task_name, priority, status, assigned_to
    FROM task_tracker
    """
    conditions = []
    values = []
    
    if task_id:
        conditions.append("id = %s")
        values.append(int(task_id))

    if task_name:
        conditions.append("LOWER(task_name) = LOWER(%s)")
        values.append(task_name)

    if priority:
        conditions.append("LOWER(priority) = LOWER(%s)")
        values.append(priority)

    if status:
        conditions.append("LOWER(status) = LOWER(%s)")
        values.append(status)

    if assigned_to:
        conditions.append("LOWER(assigned_to) = LOWER(%s)")
        values.append(assigned_to)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                tasks = cursor.fetchall()
                
                return jsonify(tasks), 200

    except psycopg.Error:
        return jsonify({"error": "database error"}), 500


@app.route("/tasks/<int:t_id>", methods=["GET"])
def get_task_by_id(t_id): 
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, task_name, priority, status, assigned_to
                    FROM task_tracker
                    WHERE id = %s
                    """,
                    (t_id, )
                )
                
                task = cursor.fetchone()

                if task is not None:
                    return jsonify(task), 200

                return jsonify({"error": "task not found"}), 404
        
    except psycopg.Error:
        return jsonify({"error": "database error"}), 500


@app.route("/tasks/<int:t_id>", methods=["PATCH"])
def update_task_by_id(t_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "no data provided"}), 400
    
    valid_statuses = {"not yet started", "ongoing", "completed"}
    valid_priorities = {"routine", "urgent"}
    
    allowed_fields = {"task_name", "priority", "status", "assigned_to"}
    updates = []
    values = []
    
    for field, value in data.items():
        if field not in allowed_fields:
            return jsonify({"error": f"invalid field: {field}"}), 400
        
        if not isinstance(value, str):
            return jsonify({"error": f"{field} must be a string"}), 400
        
        value = value.strip()
        if not value:
            return jsonify({"error": f"{field} cannot be empty"}), 400
        
        if field == "priority" and value not in valid_priorities:
            return jsonify({"error": "priority must be either 'routine' or 'urgent'"}), 400

        if field == "status" and value not in valid_statuses:
            return jsonify({"error": "status must be 'not yet started', 'ongoing' or 'completed'"}), 400
        
        updates.append(f"{field} = %s")
        values.append(value)

    if not updates:
        return jsonify({"error": "no valid fields provided"}), 400
    
    values.append(t_id)
    
    query = (
    "UPDATE task_tracker SET "
    + ", ".join(updates)
    + " WHERE id = %s "
    + "RETURNING id, task_name, priority, status, assigned_to;"
    )

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                updated_task = cursor.fetchone()

                if updated_task is None:
                    return jsonify({"error": "task not found"}), 404

                return jsonify(updated_task), 200

    except psycopg.Error:
        return jsonify({"error": "database error"}), 500
        
    

@app.route("/tasks/<int:t_id>", methods=["DELETE"])
def delete_task_by_id(t_id):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM task_tracker
                    WHERE id = %s
                    RETURNING id;
                    """,
                    (t_id, )
                )

                deleted_task = cursor.fetchone()
                
                if deleted_task is not None:
                    return jsonify({"message": f"task {t_id} deleted successfully"}), 200
                
                return jsonify({"error": "task not found"}), 404
                
    except psycopg.Error:
        return jsonify({"error": "database error"}), 500
    
if __name__ == "__main__":
    create_table()
    app.run(debug=False)



