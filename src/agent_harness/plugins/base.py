from abc import ABC, abstractmethod


class BasePlugin(ABC):
    name: str

    @abstractmethod
    def register(self, harness):
        raise NotImplementedError


class ToolPlugin(BasePlugin):
    pass


class PolicyPlugin(BasePlugin):
    pass


class FeedbackPlugin(BasePlugin):
    pass

