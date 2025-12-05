from locust import HttpUser, task, between

class TriageUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def load_main_page(self):
        self.client.get("/")

    @task
    def health_check(self):
        self.client.get("/_stcore/health")
