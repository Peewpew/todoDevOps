import json
from flask import Flask, request, render_template, redirect, url_for, jsonify, abort
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import config

app = Flask(__name__)


# #################### Config ##########################
# security mechanisms used in web applications to protect against Cross-Site Request 
app.secret_key = "set your JWT_SECRET_KEY"
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "set your JWT_SECRET_KEY"
jwt = JWTManager(app)
jwt_token = ""

def read_tasks():
    try:
        with open(config.filename, "r") as file:
            tasks = json.load(file)
            return tasks
    except FileNotFoundError:
        with open(config.filename, "w") as file:
            return json.dumps({"Message": "File wasn't found. Creating a new .json file"})
    except json.JSONDecodeError:
        return {"error": "Invalid json data in file"}
   
@app.route("/login", methods=["GET"], endpoint="get_token")
def get_token():
    jwt_token = create_access_token(identity=app.config["JWT_SECRET_KEY"])
    return jsonify(token=jwt_token)


@app.route ("/", methods=["GET"])
def get_all_tasks():
        tasks = read_tasks()
        return render_template("index.html", tasks=tasks["tasks"])

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    tasks = read_tasks().get("tasks", [])
    task = next((i for i in tasks if i["id"] == task_id), None)
    if task is not None:
        return jsonify(task)

    else:
        return json.dumps({"Message": "Couldn't find a task with this ID."})

@app.route("/tasks/completed", methods=["GET"])
def list_completed_tasks():
    tasks = read_tasks()
    completed_tasks = []

    for task in tasks["tasks"]:
        if task.get("status") == "complete":
            completed_tasks.append(task)

        if not completed_tasks:
            return json.dumps("It seems no tasks are yet completed, get to it!")
    
        return render_template("completed_tasks.html", completed_tasks=completed_tasks)
            
@app.route ("/tasks", methods=["GET"])
def get_backend_tasks():
        tasks = read_tasks()
        return render_template("index.html", tasks=tasks["tasks"])

@app.route("/tasks", methods=["POST"], endpoint="add_task")
def add_task():
    tasks = read_tasks()
    task_items = tasks["tasks"]
    max_id = 0
    if not task_items:
        max_id = 1
    else:
        for task in task_items:
            if task["id"] > max_id:
                max_id = task["id"]
        max_id = max_id + 1

    

    new_task = {
        "id": max_id,
        "description": request.form.get("description"),
        "category": request.form.get("category"),
        "status": "pending"
    }
    tasks["tasks"].append(new_task)

    with open(config.filename, "w") as f:
        json.dump(tasks, f, indent=2)

    return jsonify(message="Successfuly added new task.")

    
@app.route("/tasks/<int:task_id>", methods=["DELETE"], endpoint="delete_task")
@jwt_required()
def delete_task(task_id):
    tasks = read_tasks()
    task_index = None

    for index, task in enumerate(tasks["tasks"]):
        if task["id"] == task_id:
            task_index = index
            break

    if task_index is not None:
        deleted_task = tasks["tasks"].pop(task_index)
        with open(config.filename, "w") as file:
            json.dump(tasks, file, indent=2)
        return jsonify({"Message": "The following task has been deleted", "deleted_task": deleted_task})
    else:
        return json.dumps({"Message": "Couldn't find a task with this ID."})


# Kod för att kunna köra JWT Token på frontend
'''
@app.route("/delete/<int:task_id>", methods=["POST"])
def do_delete(task_id):
    headers = {
        'Authorization': f"Bearer {jwt_token}"
    }
    request_url = request.url_root + f"/delete/{task_id}" 
    response = requests.delete(request_url, headers=headers)
    return  response.json()    
    '''
    
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    
    tasks = read_tasks()
    task_index = None

    for index, task in enumerate(tasks["tasks"]):
        if task["id"] == task_id:
            task_index = index
            break

    if task_index is not None:
        new_task_description = request.form.get("description", tasks["tasks"][task_index].get("description"))
        
        tasks["tasks"][task_index]["description"] = new_task_description

        new_task_category = request.form.get("category", tasks["tasks"][task_index].get("category"))
        
        tasks["tasks"][task_index]["category"] = new_task_category
        
        with open(config.filename, "w") as file:
            json.dump(tasks, file, indent=2)

        updated_task = tasks["tasks"][task_index]
        #return jsonify({msg= "Task has been updated", "updated_task": updated_task})
        return jsonify(status = 200, msg= "Task has been updated", updated_task = updated_task)
    else:
        #return json.dumps({"Message": "Couldn't find a task with this ID."})
        return jsonify(status = 201, msg= "Failed")

@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def change_task_status(task_id):
    tasks = read_tasks()
    task_index = None

    for index, task in enumerate(tasks["tasks"]):
        if task["id"] == task_id:
            task_index = index
            break

    if task_index is not None:
        current_status = tasks["tasks"][task_index]["status"]
        new_status = "completed" if current_status == "pending" else "pending"

        tasks["tasks"][task_index]["status"] = new_status

        with open(config.filename, "w") as file:
            json.dump(tasks, file, indent=2)

        updated_task = tasks["tasks"][task_index]
        message = f"Task with ID {task_id} status has been changed to {new_status}"
        return redirect('/')
    else:
        return json.dumps({"Message": "Couldn't find a task with this ID."})

@app.route("/tasks/categories/", methods=["GET"])
def list_categories():
    tasks = read_tasks()
    categories = set()

    for task in tasks["tasks"]:
        category = task.get("category")
        if category is not None:
            categories.add(category)

            categories_list = list(categories)

            return jsonify({"The current categories of tasks": categories_list})
        else:
            return json.dumps({"Message": "Couldn't find any categories. The list might be empty, or 'Category' for tasks listed is set to 'None/Null'"})

@app.route("/tasks/categories/<string:category_name>", methods=["GET"])
def list_tasks_by_category(category_name):
    tasks = read_tasks()
    tasks_in_category = []

    for task in tasks["tasks"]:
        if task.get("category") == category_name:
            tasks_in_category.append(task)
            message = f"All tasks in current category {category_name}"
            return jsonify({"message": message, "tasks_in_category": tasks_in_category})
        else:
            return json.dumps({"Message": "Couldn't find any tasks in this category."})
    
if __name__ == '__main__':
    app.run(debug=True)
