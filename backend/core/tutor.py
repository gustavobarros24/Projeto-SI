from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from core.state import ChatSessionState

T = TypeVar("T", bound=ChatSessionState)


class ITutor(ABC, Generic[T]):
    @abstractmethod
    def tutor_off_track(self, state: T) -> T:
        pass

