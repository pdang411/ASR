from abc import ABC, abstractmethod


class ExecutorAdapter(ABC):
    @abstractmethod
    def accepts(self, task):
        raise NotImplementedError()

    @abstractmethod
    def dispatch(self, task):
        raise NotImplementedError()
