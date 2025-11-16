def test_create_team_success(client):
    """Тест успешного создания команды"""
    team_data = {
        "team_name": "backend",
        "members": [
            {"user_id": "u1", "username": "Alice", "is_active": True},
            {"user_id": "u2", "username": "Bob", "is_active": True},
        ],
    }
    response = client.post("/team/add", json=team_data)
    assert response.status_code == 201
    data = response.json()
    assert data["team"]["team_name"] == "backend"
    assert len(data["team"]["members"]) == 2

    assert data["team"]["members"][0]["user_id"] == "u1"
    assert data["team"]["members"][1]["user_id"] == "u2"


def test_create_team_duplicate(client):
    """Тест создания дублирующейся команды"""
    team_data = {
        "team_name": "backend",
        "members": [{"user_id": "u1", "username": "Alice", "is_active": True}],
    }
    response = client.post("/team/add", json=team_data)
    assert response.status_code == 201
    response = client.post("/team/add", json=team_data)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "TEAM_EXISTS"


def test_create_team_updates_existing_users(client):
    """Тест обновления существующих пользователей при создании команды"""

    team_data1 = {
        "team_name": "backend",
        "members": [{"user_id": "u1", "username": "Alice", "is_active": True}],
    }
    client.post("/team/add", json=team_data1)

    team_data2 = {
        "team_name": "frontend",
        "members": [{"user_id": "u1", "username": "Alice Updated", "is_active": False}],
    }
    response = client.post("/team/add", json=team_data2)
    assert response.status_code == 201
    assert response.json()["team"]["members"][0]["username"] == "Alice Updated"
    assert response.json()["team"]["members"][0]["is_active"] == False


def test_get_team_success(client):
    """Тест успешного получения команды"""
    team_data = {
        "team_name": "backend",
        "members": [
            {"user_id": "u1", "username": "Alice", "is_active": True},
            {"user_id": "u2", "username": "Bob", "is_active": True},
        ],
    }
    client.post("/team/add", json=team_data)

    response = client.get("/team/get?team_name=backend")
    assert response.status_code == 200
    data = response.json()

    assert data["team_name"] == "backend"
    assert len(data["members"]) == 2


def test_get_team_not_found(client):
    """Тест получения несуществующей команды"""
    response = client.get("/team/get?team_name=nonexistent")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
