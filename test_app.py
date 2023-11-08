import pytest
from app import app
import config

config.filename = "task_test.json"

@pytest.fixture
def client():
    # Create a test client for the Flask app
    with app.test_client() as client:
        yield client

def test_task_all_tasks(client):
    response = client.get('/tasks')
    assert response.status_code == 200
    #response_data = response.get_json()
    #assert "tasks" in response_data

def test_tasks_post(client):
    headers = {}
    form_data = {
        "description": "detail",
        "category": "test task"
        }

    response = client.post('/tasks', data=form_data, headers=headers)
    assert response.status_code == 200

def test_tasks_put(client):
    task_id = 1
    headers = {}
    form_data = {
        "task_id": task_id,
        "description": "detail",
        "category": "test task",
        "status": "Pending"
        }

    response = client.put(f'/tasks/{task_id}', data=form_data, headers=headers)
    assert response.status_code == 200

def test_tasks_delete(client):
    task_id = 1
    headers = {}
    form_data = {}

    response = client.delete(f'/tasks/{task_id}', headers=headers)
    assert response.status_code == 200

