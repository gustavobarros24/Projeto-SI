from typing import Optional

from pydantic import BaseModel, Field

from core.state import ChatSessionState, FinalReport, Feedback
from domains.anamnesis.scoring import DiagnosisAccuracy
from utils.messages import Message


class PatientPersona(BaseModel):
    name: str
    age: int
    gender: str

class Symptom(BaseModel):
    question_id: str
    symptom: str

class Diagnosis(BaseModel):
    diagnosis_id: str
    diagnosis: str
    accuracy: DiagnosisAccuracy

class AnamnesisFeedback(Feedback):
    symptom_coverage: str = Field(
        ...,
        description="Sentence describing which symptoms were well explored and which were missed.",
    )
    diagnosis_attempts: str = Field(
        ..., 
        description="Sentence explaining why the diagnosis was incorrect and what makes the correct diagnosis more appropriate.",
    )

class AnamnesisFinalReport(FinalReport):
    hidden_diagnosis: str
    covered_symptoms_num: int
    all_symptoms_num: int
    all_symptoms: list[str]
    covered_symptoms: list[str]

class EvaluationSheet(BaseModel):
    covered_symptoms: list[Symptom] = Field(default_factory=list)
    diagnosis: list[Diagnosis] = Field(default_factory=list)

    @property
    def covered_symptoms_num(self) -> int:
        return len(self.covered_symptoms)

    def already_covered(self, symptom: str) -> bool:
        return any(s.symptom.lower() == symptom.lower() for s in self.covered_symptoms)

class AnamnesisSessionState(ChatSessionState):
    diagnosis_attempts: list[Message] = Field(default_factory=list)

    # case selection (mirrors orchestrator state)
    anamnesis_case_id: Optional[str] = None

    # patient
    patient_persona: Optional[PatientPersona] = None
    hidden_diagnosis: str = ""
    all_symptoms: list[str] = Field(default_factory=list)
    patient_emotional_state: str = ""

    # evaluation
    evaluation_sheet: EvaluationSheet = Field(default_factory=EvaluationSheet)

    @property
    def diagnosis_attempts_num(self) -> int:
        return len(self.diagnosis_attempts)

    @property
    def student_diagnosis(self) -> list[str]:
        return [d.diagnosis for d in self.evaluation_sheet.diagnosis]

    @property
    def student_covered_symptoms(self) -> list[str]:
        return [s.symptom for s in self.evaluation_sheet.covered_symptoms]
