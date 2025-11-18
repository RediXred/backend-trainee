from locust import HttpUser, task, between
import random
import string


def generate_random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class PRReviewerUser(HttpUser):
    """Пользователь для нагрузочного тестирования"""

    wait_time = between(1, 3)

    def on_start(self):
        self.team_name = f"team_{generate_random_string()}"
        self.user_ids = [f"u{i}" for i in range(1, 6)]

        team_data = {
            "team_name": self.team_name,
            "members": [
                {"user_id": user_id, "username": f"User_{user_id}", "is_active": True}
                for user_id in self.user_ids
            ],
        }

        response = self.client.post("/team/add", json=team_data)
        if response.status_code not in [201, 400]:
            print(f"Failed to create team: {response.status_code}")

        self.created_prs = []

    @task(3)
    def create_team(self):
        team_name = f"team_{generate_random_string()}"
        team_data = {
            "team_name": team_name,
            "members": [
                {
                    "user_id": f"u_{generate_random_string()}",
                    "username": f"User_{generate_random_string()}",
                    "is_active": True,
                }
                for _ in range(random.randint(2, 5))
            ],
        }
        with self.client.post("/team/add", json=team_data, catch_response=True) as response:
            if response.status_code in [201, 400]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(5)
    def get_team(self):
        with self.client.get(
            f"/team/get?team_name={self.team_name}", catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(4)
    def create_pr(self):
        if not self.user_ids:
            return

        pr_id = f"pr_{generate_random_string()}"

        pr_data = {
            "pull_request_id": pr_id,
            "pull_request_name": f"Feature {generate_random_string()}",
            "author_id": random.choice(self.user_ids),
        }

        with self.client.post("/pullRequest/create", json=pr_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                self.created_prs.append(pr_id)
            elif response.status_code in [404, 409]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(3)
    def merge_pr(self):
        if not self.created_prs:
            pr_id = f"pr_{generate_random_string()}"
        else:
            pr_id = random.choice(self.created_prs)

        merge_data = {"pull_request_id": pr_id}
        with self.client.post(
            "/pullRequest/merge", json=merge_data, catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(2)
    def reassign_reviewer(self):
        if not self.created_prs or not self.user_ids:
            return

        pr_id = random.choice(self.created_prs)
        old_user_id = random.choice(self.user_ids)

        reassign_data = {"pull_request_id": pr_id, "old_user_id": old_user_id}

        with self.client.post(
            "/pullRequest/reassign", json=reassign_data, catch_response=True
        ) as response:
            if response.status_code in [200, 404, 409]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(2)
    def set_user_active(self):
        if not self.user_ids:
            return

        user_id = random.choice(self.user_ids)
        request_data = {"user_id": user_id, "is_active": random.choice([True, False])}

        with self.client.post(
            "/users/setIsActive", json=request_data, catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def bulk_deactivate_users(self):
        """Массовая деактивация пользователей команды"""
        if not self.user_ids or len(self.user_ids) < 2:
            return

        num_to_deactivate = random.randint(1, max(1, len(self.user_ids) // 2))
        users_to_deactivate = random.sample(self.user_ids, num_to_deactivate)

        request_data = {"team_name": self.team_name, "user_ids": users_to_deactivate}

        with self.client.post(
            "/users/bulkDeactivate", json=request_data, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                data = response.json()
                if "deactivated_users" in data and "reassigned_prs" in data:
                    response.success()
                else:
                    response.failure("Missing expected fields in response")
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(3)
    def get_user_reviews(self):
        if not self.user_ids:
            return

        user_id = random.choice(self.user_ids)
        with self.client.get(
            f"/users/getReview?user_id={user_id}", catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(5)
    def get_statistics(self):
        """Получение статистики"""
        with self.client.get("/statistics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(10)
    def health_check(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
