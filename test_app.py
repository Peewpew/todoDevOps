import pytest
from app import app
import config

config.filename = "task_test.json"

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_task_all_tasks(client):
    response = client.get('/tasks')
    assert response.status_code == 200

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
        "description": "testing desc",
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

def test_tasks_update(client):
    task_id = 1
    headers = {}
    form_data = {
        "description": "New description",
        "category": "New category"
    }

    response = client.put(f'/tasks/{task_id}', data=form_data, headers=headers)
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data['status'] == 200
    assert response_data['msg'] == 'Task has been updated'
    updated_task = response_data['updated_task']
    assert updated_task['description'] == 'New description'
    assert updated_task['category'] == 'New category'

def test_change_task_status(client):
    task_id = 1
    headers = {}
    form_data = {
        "task_id": task_id,
        "description": "testing desc",
        "category": "test task",
        "status": "Pending"
    }

    response = client.put(f'/tasks/{task_id}/complete', data=form_data, headers=headers)
    assert response.status_code == 200

def test_list_categories(client):
    task_id = 1
    headers = {}
    form_data = {
        "task_id": task_id,
        "description": "testing desc",
        "category": "test task",
        "status": "Pending",
         "task_id": 2,
        "description": "testing desc",
        "category": "test task",
        "status": "Pending"
    }
    response = client.get('/tasks/categories/')
    assert response.status_code == 200
    
def test_list_tasks_by_category(client):
    task_id = 1
    headers = {}
    form_data = {
        "task_id": task_id,
        "description": "testing desc",
        "category": "test task",
        "status": "Pending",
         "task_id": 2,
        "description": "testing desc",
        "category": "test task",
        "status": "Pending"
    }
    response = client.get('/tasks/categories/Category A')
    assert response.status_code == 200    