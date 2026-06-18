def register_and_login(client, username="testuser", password="secret123"):
    client.post(
        "/register",
        json={"username": username, "password": password}
    )

    login_response = client.post(
        "/login",
        data={"username": username, "password": password}
    )

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

def test_create_task(client):
    headers = register_and_login(client)
    response = client.post(
        "/tasks",
        json={"title": "Test Task", "done": False},
        headers = headers
    )

    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Test Task"
    assert data["done"] is False
    assert "id" in data


def test_get_tasks(client):
    headers = register_and_login(client)

    client.post(
        "/tasks",
        json={"title": "Task 1", "done": False},
        headers=headers
    )

    response = client.get("/tasks", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_duplicate_title(client):
    headers = register_and_login(client)

    client.post(
        "/tasks",
        json={"title": "Duplicate", "done": False},
        headers=headers
    )

    response = client.post(
        "/tasks",
        json={"title": "Duplicate", "done": False},
        headers=headers
    )

    assert response.status_code == 409


def test_get_nonexistent_task(client):
    headers = register_and_login(client)

    response = client.get("/tasks/999", headers=headers)

    assert response.status_code == 404


def test_delete_task(client):
    headers = register_and_login(client)

    create = client.post(
        "/tasks",
        json={"title": "Delete Me", "done": False},
        headers=headers
    )
    task_id = create.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers=headers)

    assert response.status_code == 204


def test_put_task_updates_title_and_done(client):
    headers = register_and_login(client)

    create = client.post(
        "/tasks",
        json={"title": "Original", "done": False},
        headers=headers
    )
    task_id = create.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated", "done": True},
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated"
    assert data["done"] is True


def test_patch_task_updates_single_field(client):
    headers = register_and_login(client)

    create = client.post(
        "/tasks",
        json={"title": "Patch Me", "done": False},
        headers=headers
    )
    task_id = create.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"done": True},
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Patch Me"
    assert data["done"] is True


def test_patch_empty_body_returns_400(client):
    headers = register_and_login(client)

    create = client.post(
        "/tasks",
        json={"title": "No Fields", "done": False},
        headers=headers
    )
    task_id = create.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={}, headers=headers)

    assert response.status_code == 400


def test_timestamps_created_at_constant_updated_at_changes_on_patch(client):
    headers = register_and_login(client)

    create = client.post(
        "/tasks",
        json={"title": "Time Test", "done": False},
        headers=headers
    )
    task_id = create.json()["id"]

    created_data = create.json()
    created_at_1 = created_data["created_at"]
    updated_at_1 = created_data["updated_at"]

    patch = client.patch(
        f"/tasks/{task_id}",
        json={"done": True},
        headers=headers
    )
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


def test_users_only_see_their_own_tasks(client):
    user1_headers = register_and_login(
        client,
        username="user1",
        password="secret123"
    )

    user2_headers = register_and_login(
        client,
        username="user2",
        password="secret123"
    )

    client.post(
        "/tasks",
        json={"title": "User 1 Task", "done": False},
        headers=user1_headers
    )

    response = client.get("/tasks", headers=user2_headers)

    assert response.status_code == 200
    assert response.json() == []