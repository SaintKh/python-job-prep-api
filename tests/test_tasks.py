def test_create_task(client):
    response = client.post(
        "/tasks",
        json={"title": "Test Task", "done": False}
    )

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test Task"
    assert data["done"] is False
    assert "id" in data


def test_get_tasks(client):
    client.post("/tasks", json={"title": "Task 1", "done": False})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_duplicate_title(client):
    client.post("/tasks", json={"title": "Duplicate", "done": False})

    response = client.post("/tasks", json={"title": "Duplicate", "done": False})

    assert response.status_code == 409


def test_get_nonexistent_task(client):
    response = client.get("/tasks/999")

    assert response.status_code == 404


def test_delete_task(client):
    create = client.post("/tasks", json={"title": "Delete Me", "done": False})
    task_id = create.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
