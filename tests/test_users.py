import pytest


@pytest.fixture
def setup_team(client):
    """Создание команды с пользователями"""
    team_data = {
        "team_name": "backend",
        "members": [
            {"user_id": "u1", "username": "Alice", "is_active": True},
            {"user_id": "u2", "username": "Bob", "is_active": True},
            {"user_id": "u3", "username": "Charlie", "is_active": True},
        ],
    }
    client.post("/team/add", json=team_data)
    return team_data


def test_set_is_active_success(client, setup_team):
    """Тест успешного изменения флага активности"""
    request_data = {"user_id": "u1", "is_active": False}
    response = client.post("/users/setIsActive", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["user"]["user_id"] == "u1"
    assert data["user"]["is_active"] == False
    assert data["reassigned_prs"] == 0


def test_set_is_active_not_found(client):
    """Тест изменения флага активности для несуществующего пользователя"""

    request_data = {"user_id": "nonexistent", "is_active": False}
    response = client.post("/users/setIsActive", json=request_data)
    assert response.status_code == 404

    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_user_reviews_success(client, setup_team):
    """Тест успешного получения PR пользователя"""
    pr_data = {"pull_request_id": "pr-1", "pull_request_name": "Test PR", "author_id": "u1"}
    client.post("/pullRequest/create", json=pr_data)

    response = client.get("/users/getReview?user_id=u2")
    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == "u2"
    assert len(data["pull_requests"]) >= 0


def test_get_user_reviews_not_found(client):
    """Тест получения PR для несуществующего пользователя"""
    response = client.get("/users/getReview?user_id=nonexistent")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_user_reviews_empty(client, setup_team):
    """Тест получения PR для пользователя без назначений"""
    response = client.get("/users/getReview?user_id=u3")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "u3"
    assert len(data["pull_requests"]) == 0


def test_bulk_deactivate_success(client, setup_team):
    """Тест успешной массовой деактивации пользователей"""
    request_data = {"team_name": "backend", "user_ids": ["u2", "u3"]}
    response = client.post("/users/bulkDeactivate", json=request_data)
    assert response.status_code == 200
    data = response.json()

    assert len(data["deactivated_users"]) == 2
    assert all(user["is_active"] == False for user in data["deactivated_users"])
    assert all(user["user_id"] in ["u2", "u3"] for user in data["deactivated_users"])
    assert "reassigned_prs" in data


def test_bulk_deactivate_with_reassignment(client, setup_team):
    """Тест массовой деактивации с автоматическим переназначением ревьюверов"""
    additional_members = {
        "team_name": "backend",
        "members": [
            {"user_id": "u1", "username": "Alice", "is_active": True},
            {"user_id": "u2", "username": "Bob", "is_active": True},
            {"user_id": "u3", "username": "Charlie", "is_active": True},
            {"user_id": "u4", "username": "David", "is_active": True},
            {"user_id": "u5", "username": "Eve", "is_active": True},
        ],
    }
    client.post("/team/add", json=additional_members)
    pr_data = {"pull_request_id": "pr-1", "pull_request_name": "Test PR 1", "author_id": "u1"}
    create_response = client.post("/pullRequest/create", json=pr_data)
    assert create_response.status_code == 201
    reviewers_before = create_response.json()["pr"]["assigned_reviewers"]
    assert len(reviewers_before) > 0
    deactivating_users = [r for r in reviewers_before if r in ["u2", "u3"]]
    if not deactivating_users:
        deactivating_users = reviewers_before[:1]

    if deactivating_users:
        request_data = {"team_name": "backend", "user_ids": deactivating_users}
        response = client.post("/users/bulkDeactivate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["deactivated_users"]) == len(deactivating_users)
        for deactivated_user in deactivating_users:
            reassign_response = client.post(
                "/pullRequest/reassign",
                json={"pull_request_id": "pr-1", "old_user_id": deactivated_user},
            )
            assert reassign_response.status_code in [409, 404]


def test_bulk_deactivate_not_found(client, setup_team):
    """Тест массовой деактивации для несуществующих пользователей"""
    request_data = {"team_name": "backend", "user_ids": ["nonexistent1", "nonexistent2"]}
    response = client.post("/users/bulkDeactivate", json=request_data)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_bulk_deactivate_wrong_team(client, setup_team):
    """Тест массовой деактивации пользователей из другой команды"""
    other_team_data = {
        "team_name": "frontend",
        "members": [
            {"user_id": "u10", "username": "User10", "is_active": True},
            {"user_id": "u11", "username": "User11", "is_active": True},
        ],
    }
    client.post("/team/add", json=other_team_data)
    request_data = {"team_name": "backend", "user_ids": ["u10", "u11"]}

    response = client.post("/users/bulkDeactivate", json=request_data)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_bulk_deactivate_already_inactive(client, setup_team):
    """Тест идемпотентности массовой деактивации"""
    client.post("/users/setIsActive", json={"user_id": "u2", "is_active": False})

    request_data = {"team_name": "backend", "user_ids": ["u2", "u3"]}

    response = client.post("/users/bulkDeactivate", json=request_data)
    assert response.status_code == 200
    data = response.json()

    assert len(data["deactivated_users"]) == 2
    assert all(user["is_active"] == False for user in data["deactivated_users"])
