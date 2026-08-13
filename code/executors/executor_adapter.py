from abc import ABC, abstractmethod

class ExecutorAdapter(ABC):

    @abstractmethod
    def accepts(self, task):
        ...

    @abstractmethod
    def dispatch(self, task):
        ...