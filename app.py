from flask import Flask, request, jsonify
from database import init_db
from models import Task
import requests
from pydantic import BaseModel, ValidationError

app = Flask(__name__)
init_db(app)

class TaskModel(BaseModel):
    title: str
    description: str = None

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        task_data = TaskModel(**request.json)
        new_task = Task(title=task_data.title, description=task_data.description)
        db.session.add(new_task)
        db.session.commit()
        return jsonify(new_task.to_dict()), 201
    except ValidationError as e:
        return jsonify(e.errors()), 400

@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks]), 200

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    try:
        task_data = TaskModel(**request.json)
        task.title = task_data.title
        task.description = task_data.description
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except ValidationError as e:
        return jsonify(e.errors()), 400

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204

@app.route('/external-tasks', methods=['GET'])
def get_external_tasks():
    external_api_url = 'https://jsonplaceholder.typicode.com/todos'
    response = requests.get(external_api_url)
    tasks = response.json()
    return jsonify(tasks), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
