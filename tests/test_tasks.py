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

def test_put_task_updates_title_and_done(client):
    create = client.post("/tasks", json={"title": "Original", "done": False})
    task_id = create.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"title": "Updated", "done": True})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated"
    assert data["done"] is True


def test_patch_task_updates_single_field(client):
    create = client.post("/tasks", json={"title": "Patch Me", "done": False})
    task_id = create.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"done": True})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Patch Me"   # unchanged
    assert data["done"] is True


def test_patch_empty_body_returns_400(client):
    create = client.post("/tasks", json={"title": "No Fields", "done": False})
    task_id = create.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={})

    assert response.status_code == 400


def test_timestamps_created_at_constant_updated_at_changes_on_patch(client):
    create = client.post("/tasks", json={"title": "Time Test", "done": False})
    task_id = create.json()["id"]

    created_data = create.json()
    created_at_1 = created_data["created_at"]
    updated_at_1 = created_data["updated_at"]

    patch = client.patch(f"/tasks/{task_id}", json={"done": True})
    assert patch.status_code == 200

    patched_data = patch.json()
    created_at_2 = patched_data["created_at"]
    updated_at_2 = patched_data["updated_at"]

    assert created_at_2 == created_at_1
    assert updated_at_2 != updated_at_1

def test_register_user(client):
    response = client.post(
        "/register",
        json={"username": "khalil", "password": "secret123"}
    )

    assert response.status_code == 201
    data = response.json()

    assert data["username"] == "khalil"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_username(client):
    client.post(
        "/register",
        json={"username": "khalil", "password": "secret123"}
    )

    response = client.post(
        "/register",
        json={"username": "khalil", "password": "secret123"}
    )

    assert response.status_code == 409


def test_register_short_password_fails(client):
    response = client.post(
        "/register",
        json={"username": "khalil", "password": "123"}
    )

    assert response.status_code == 422

def test_login_success(client):
    client.post(
        "/register",
        json={"username": "testuser", "password": "secret123"}
    )

    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "secret123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/register",
        json={"username": "testuser", "password": "secret123"}
    )

    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_me_requires_auth(client):
    response = client.get("/me")

    assert response.status_code == 401

def test_me_with_valid_token(client):
    client.post(
        "/register",
        json={"username": "testuser", "password": "secret123"}
    )

    login_response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "secret123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data