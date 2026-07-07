class HealingState:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.failures = 0
        self.last_category: str | None = None
        self.should_escalate = False

    def record_failure(self, category: str) -> bool:
        self.failures += 1
        self.last_category = category
        self.should_escalate = self.failures >= self.max_retries
        return self.should_escalate

    def record_success(self):
        self.failures = 0
        self.last_category = None
        self.should_escalate = False

