
from flask import Flask, jsonify, request
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "nexus_systems_task_tracker.db"

app = Flask(__name__)

def create_table(db_path):
    try:
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS task_tracker (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                assigned_to TEXT NOT NULL);""")
            
    except sqlite3.Error as e:
        print(f"Error: {e}")   

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
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO task_tracker (task_name, priority, status, assigned_to) \
                VALUES (?,?,?,?)", (task_name, priority, status, assigned_to))
            
            return jsonify({
                "id": cur.lastrowid,
                "task_name": task_name,
                "priority": priority,
                "status": status,
                "assigned_to": assigned_to
            }), 201
            
    except sqlite3.Error:
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
        conditions.append("id = ?")
        values.append(int(task_id))
        
    if task_name:
        conditions.append("LOWER(task_name) = LOWER(?)")
        values.append(task_name)    
        
    if priority:
        conditions.append("LOWER(priority) = LOWER(?)")
        values.append(priority)
    
    if status:
        conditions.append("LOWER(status) = LOWER(?)")
        values.append(status)
        
    if assigned_to:
        conditions.append("LOWER(assigned_to) = LOWER(?)")
        values.append(assigned_to)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(query, values)
            rows = cur.fetchall()
            tasks = [dict(row) for row in rows]
            
            return jsonify(tasks), 200

    except sqlite3.Error:
        return jsonify({"error": "database error"}), 500


@app.route("/tasks/<int:t_id>", methods=["GET"])
def get_task_by_id(t_id): 
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute("SELECT id, task_name, priority, status, assigned_to FROM task_tracker \
                        WHERE id = ?", (t_id, ))
            row = cur.fetchone()
            if row is not None:
                return jsonify(dict(row)), 200
            
            return jsonify({"error": "task not found"}), 404
        
    except sqlite3.Error:
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
        
        updates.append(f"{field} = ?")
        values.append(value)

    if not updates:
        return jsonify({"error": "no valid fields provided"}), 400
    
    values.append(t_id)
    
    query = "UPDATE task_tracker SET " + ", ".join(updates) + " WHERE id = ?"
    
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(query, values)
            if cur.rowcount == 0:
                return jsonify({"error": "task not found"}), 404

            cur.execute("SELECT id, task_name, priority, status, assigned_to FROM task_tracker WHERE id = ?",
                        (t_id, ))
            row = cur.fetchone()
            
            return jsonify(dict(row)), 200

    
    except sqlite3.Error:
        return jsonify({"error":"database error"}), 500
    
    

@app.route("/tasks/<int:t_id>", methods=["DELETE"])
def delete_task_by_id(t_id):
    try:
        with sqlite3.connect(DATABASE) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM task_tracker WHERE id = ?", (t_id, ))
            if cur.rowcount == 1:
                return jsonify({"message": f"task {t_id} deleted successfully"}), 200
            
            return jsonify({"error": "task not found"}), 404
        
    except sqlite3.Error:
        return jsonify({"error": "database error"}), 500
    
if __name__ == "__main__":
    create_table(DATABASE)
    app.run(debug=False)



