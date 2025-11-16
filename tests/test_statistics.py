import pytest


@pytest.fixture
def setup_team_and_prs(client):
    """Создание команды и нескольких PR"""

    team_data = {
        "team_name": "backend",
        "members": [
            {"user_id": "u1", "username": "Alice", "is_active": True},
            {"user_id": "u2", "username": "Bob", "is_active": True},
            {"user_id": "u3", "username": "Charlie", "is_active": True},
        ],
    }
    client.post("/team/add", json=team_data)

    pr1_data = {"pull_request_id": "pr-1", "pull_request_name": "Feature 1", "author_id": "u1"}
    client.post("/pullRequest/create", json=pr1_data)
    pr2_data = {"pull_request_id": "pr-2", "pull_request_name": "Feature 2", "author_id": "u2"}
    client.post("/pullRequest/create", json=pr2_data)
    client.post("/pullRequest/merge", json={"pull_request_id": "pr-1"})

    return team_data


def test_get_statistics_success(client, setup_team_and_prs):
    """Тест успешного получения статистики"""
    response = client.get("/statistics")
    assert response.status_code == 200
    data = response.json()

    assert "pr_stats" in data
    assert "user_review_stats" in data

    pr_stats = data["pr_stats"]
    assert pr_stats["total_prs"] == 2
    assert pr_stats["open_prs"] == 1
    assert pr_stats["merged_prs"] == 1

    user_stats = data["user_review_stats"]
    assert isinstance(user_stats, list)
    if len(user_stats) > 1:
        for i in range(len(user_stats) - 1):
            assert user_stats[i]["assignments_count"] >= user_stats[i + 1]["assignments_count"]


def test_get_statistics_empty(client):
    """Тест получения статистики для пустой БД"""
    response = client.get("/statistics")
    assert response.status_code == 200
    data = response.json()

    assert data["pr_stats"]["total_prs"] == 0
    assert data["pr_stats"]["open_prs"] == 0
    assert data["pr_stats"]["merged_prs"] == 0

    assert len(data["user_review_stats"]) == 0
