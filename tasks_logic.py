"""
tasks_logic.py — CRUD Logic for Tasks

All functions return dictionaries that Flask can easily convert to JSON.
Example: return {"message": "...", "success": True/False}

Your Flask route just needs to do:
    from tasks_logic import create_task, get_user_tasks
    result = create_task(user_id, title, content)
    return jsonify(result), result["status"]
"""

from datetime import datetime
from database import tasks_db, get_next_task_id


# ── CREATE — Add a new task ──
def create_task(user_id, title, content=""):
    """
    Creates a new task for the given user.
    Returns dict with message, the new task, and status code.
    """

    if not title or not title.strip():
        return {"message": "Task title cannot be empty.", "success": False, "status": 400}

    new_task = {
        "id": get_next_task_id(),
        "title": title.strip(),
        "content": content.strip(),
        "done": False,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "user_id": user_id,
    }
    tasks_db.append(new_task)

    return {"message": "Task created!", "success": True, "task": new_task, "status": 201}


# ── READ — Get all tasks for a specific user ──
def get_user_tasks(user_id):
    """
    Returns all tasks belonging to the given user.
    Sorted newest first.
    """
    my_tasks = []
    for task in tasks_db:
        if task["user_id"] == user_id:
            my_tasks.append(task)

    # Sort newest first
    my_tasks.reverse()

    return {"tasks": my_tasks, "success": True, "status": 200}


# ── UPDATE — Edit a task's title and content ──
def update_task(user_id, task_id, new_title, new_content=""):
    """
    Finds the task by ID and updates it.
    Only the task owner can edit it.
    """
    if not new_title or not new_title.strip():
        return {"message": "Task title cannot be empty.", "success": False, "status": 400}

    for task in tasks_db:
        if task["id"] == task_id:

            if task["user_id"] != user_id:
                return {"message": "Access denied.", "success": False, "status": 403}

            task["title"]   = new_title.strip()
            task["content"] = new_content.strip()
            return {"message": "Task updated!", "success": True, "task": task, "status": 200}

    return {"message": "Task not found.", "success": False, "status": 404}


# ── DELETE — Remove a task ──
def delete_task(user_id, task_id):
    """
    Finds the task by ID and removes it.
    Only the task owner can delete it.
    """
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:

            if task["user_id"] != user_id:
                return {"message": "Access denied.", "success": False, "status": 403}

            tasks_db.pop(i)
            return {"message": "Task deleted.", "success": True, "status": 200}

    return {"message": "Task not found.", "success": False, "status": 404}


# ── TOGGLE — Mark a task as done or not done ──
def toggle_task(user_id, task_id):
    """
    Flips the done status: True → False, or False → True.
    """
    for task in tasks_db:
        if task["id"] == task_id:

            if task["user_id"] != user_id:
                return {"message": "Access denied.", "success": False, "status": 403}

            task["done"] = not task["done"]
            status = "done" if task["done"] else "not done"
            return {"message": f"Task marked as {status}.", "success": True, "task": task, "status": 200}

    return {"message": "Task not found.", "success": False, "status": 404}


# ============================================================
# ── TEST IT ──
# ============================================================
if __name__ == "__main__":
    from database import print_all_data

    test_user_id = 1

    print("=" * 50)
    print("CREATE — Adding tasks")
    print("=" * 50)

    result = create_task(test_user_id, "Buy groceries", "Milk, eggs, bread")
    print(f"  {result['message']}")

    result = create_task(test_user_id, "Finish homework")
    print(f"  {result['message']}")

    result = create_task(test_user_id, "Call the dentist", "Appointment for next week")
    print(f"  {result['message']}")

    result = create_task(test_user_id, "")
    print(f"  {result['message']}")

    print()
    print("=" * 50)
    print("READ — My tasks")
    print("=" * 50)
    result = get_user_tasks(test_user_id)
    for task in result["tasks"]:
        check = "✓" if task["done"] else " "
        print(f"  [{check}] #{task['id']} — {task['title']}")

    print()
    print("=" * 50)
    print("UPDATE — Editing task #1")
    print("=" * 50)
    result = update_task(test_user_id, 1, "Buy groceries and snacks", "Milk, eggs, bread, chips")
    print(f"  {result['message']}")

    print()
    print("=" * 50)
    print("TOGGLE — Marking task #2 as done")
    print("=" * 50)
    result = toggle_task(test_user_id, 2)
    print(f"  {result['message']}")

    print()
    print("=" * 50)
    print("DELETE — Removing task #3")
    print("=" * 50)
    result = delete_task(test_user_id, 3)
    print(f"  {result['message']}")

    print()
    print_all_data()
