from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Final
from enum import Enum

from pydantic import Field, BaseModel

from core.state import ChatSessionState

MAX_POINTS: Final[int] = 100
T = TypeVar("T", bound=ChatSessionState)

class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"

def get_grade(points: float) -> Grade:
    if points >= 90:
        return Grade.A
    elif points >= 75:
        return Grade.B
    elif points >= 60:
        return Grade.C
    elif points >= 50:
        return Grade.D
    return Grade.F

class InputEvaluation(BaseModel):
    is_relevant: bool = Field(..., description="Indicates whether the question is relevant to the clinical case.")

class IEvaluator(ABC, Generic[T]):
    @abstractmethod
    def generate_final_report(self, state: T) -> T:
        pass

    @abstractmethod
    def evaluate_input(self, state: T) -> T:
        pass

