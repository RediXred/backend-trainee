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
            {"user_id": "u4", "username": "David", "is_active": True},
        ],
    }
    client.post("/team/add", json=team_data)
    return team_data


def test_create_pr_success(client, setup_team):
    """Тест успешного создания PR"""
    pr_data = {"pull_request_id": "pr-1", "pull_request_name": "Add feature", "author_id": "u1"}
    response = client.post("/pullRequest/create", json=pr_data)
    assert response.status_code == 201
    data = response.json()
    assert data["pr"]["pull_request_id"] == "pr-1"
    assert data["pr"]["pull_request_name"] == "Add feature"
    assert data["pr"]["author_id"] == "u1"
    assert data["pr"]["status"] == "OPEN"
    assert "assigned_reviewers" in data["pr"]
    assert len(data["pr"]["assigned_reviewers"]) <= 2


def test_create_pr_duplicate(client, setup_team):
    """Тест создания дублирующегося PR"""
    pr_data = {"pull_request_id": "pr-1", "pull_request_name": "Add feature", "author_id": "u1"}

    response = client.post("/pullRequest/create", json=pr_data)
    assert response.status_code == 201
    response = client.post("/pullRequest/create", json=pr_data)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PR_EXISTS"


def test_create_pr_author_not_found(client):
    """Тест создания PR с несуществующим автором"""
    pr_data = {
        "pull_request_id": "pr-1",
        "pull_request_name": "Add feature",
        "author_id": "nonexistent",
    }
    response = client.post("/pullRequest/create", json=pr_data)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_merge_pr_success(client, setup_team):
    """Тест успешного мерджа PR"""
    pr_data = {"pull_request_id": "pr-1", "pull_request_name": "Add feature", "author_id": "u1"}
    client.post("/pullRequest/create", json=pr_data)

    merge_data = {"pull_request_id": "pr-1"}
    response = client.post("/pullRequest/merge", json=merge_data)
    assert response.status_code == 200
    data = response.json()
    assert data["pr"]["status"] == "MERGED"
    assert data["pr"]["mergedAt"] is not None


def test_merge_pr_idempotent(client, setup_team):
    """Тест идемпотентности merge PR"""
    pr_data = {"pull_request_id": "pr-1", "pull_request_name": "Add feature", "author_id": "u1"}
    client.post("/pullRequest/create", json=pr_data)
    merge_data = {"pull_request_id": "pr-1"}
    response1 = client.post("/pullRequest/merge", json=merge_data)
    assert response1.status_code == 200

    response2 = client.post("/pullRequest/merge", json=merge_data)
    assert response2.status_code == 200
    assert response2.json()["pr"]["status"] == "MERGED"


def test_merge_pr_not_found(client):
    """Тест merge несуществующего PR"""
    merge_data = {"pull_request_id": "nonexistent"}
    response = client.post("/pullRequest/merge", json=merge_data)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_reassign_reviewer_success(client, setup_team):
    """Тест успешного переназначения ревьювера"""
    pr_data = {"pull_request_id": "pr-1", "pull_request_name": "Add feature", "author_id": "u1"}
    create_response = client.post("/pullRequest/create", json=pr_data)
    assigned_reviewers = create_response.json()["pr"]["assigned_reviewers"]

    if len(assigned_reviewers) > 0:
        old_reviewer = assigned_reviewers[0]

        reassign_data = {"pull_request_id": "pr-1", "old_user_id": old_reviewer}
        response = client.post("/pullRequest/reassign", json=reassign_data)
        assert response.status_code == 200
        data = response.json()
        assert "replaced_by" in data
        assert data["replaced_by"] != old_reviewer
        assert old_reviewer not in data["pr"]["assigned_reviewers"]


def test_reassign_reviewer_not_assigned(client, setup_team):
    """Тест переназначения не назначенного ревьювера"""
    pr_data = {"pull_request_id": "pr-1", "pull_request_name": "Add feature", "author_id": "u1"}
    create_response = client.post("/pullRequest/create", json=pr_data)
    assigned_reviewers = create_response.json()["pr"]["assigned_reviewers"]
    reviewer_id = assigned_reviewers[0] + "_not_exists"
    reassign_data = {"pull_request_id": "pr-1", "old_user_id": reviewer_id}
    response = client.post("/pullRequest/reassign", json=reassign_data)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "NOT_ASSIGNED"


def test_reassign_reviewer_merged_pr(client, setup_team):
    """Тест переназначения ревьювера для мердженного PR"""
    pr_data = {"pull_request_id": "pr-1", "pull_request_name": "Add feature", "author_id": "u1"}
    create_response = client.post("/pullRequest/create", json=pr_data)
    assigned_reviewers = create_response.json()["pr"]["assigned_reviewers"]

    client.post("/pullRequest/merge", json={"pull_request_id": "pr-1"})

    if len(assigned_reviewers) > 0:
        reassign_data = {"pull_request_id": "pr-1", "old_user_id": assigned_reviewers[0]}
        response = client.post("/pullRequest/reassign", json=reassign_data)
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "PR_MERGED"


def test_reassign_reviewer_no_candidate(client, setup_team):
    """Тест переназначения с NO_CANDIDATE"""

    team_data = {
        "team_name": "small_team",
        "members": [
            {"user_id": "u10", "username": "Solo", "is_active": True},
            {"user_id": "u11", "username": "Solo2", "is_active": True},
            {"user_id": "u12", "username": "Solo3", "is_active": False},
        ],
    }
    client.post("/team/add", json=team_data)

    pr_data = {"pull_request_id": "pr-2", "pull_request_name": "Add feature", "author_id": "u10"}
    client.post("/pullRequest/create", json=pr_data)

    response = client.post(
        "/pullRequest/reassign", json={"pull_request_id": "pr-2", "old_user_id": "u11"}
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "NO_CANDIDATE"
