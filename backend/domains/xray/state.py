from pydantic import BaseModel, Field

from core.state import ChatSessionState, FinalReport, Feedback
from domains.xray.scoring import ImpressionAccuracy
from utils.messages import Message


class Impression(BaseModel):
    attempt_id: str
    impression: str
    accuracy: ImpressionAccuracy

class Finding(BaseModel):
    message_id: str
    is_correct: bool
    finding: str

class EvaluationSheet(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    impressions: list[Impression] = Field(default_factory=list)

    @property
    def correct_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.is_correct]

    @property
    def correct_findings_num(self) -> int:
        return len(self.correct_findings)

    @property
    def incorrect_findings(self) -> list[Finding]:
        return [finding for finding in self.findings if not finding.is_correct]

    @property
    def incorrect_findings_num(self) -> int:
        return len(self.incorrect_findings)

    def already_found(self, finding: str) -> bool:
        return any(f.finding.lower() == finding.lower() for f in self.findings)

class XRayFeedback(Feedback):
    correct_findings_note: str = Field(
        ...,
        description="Sentence about the findings the student correctly identified, acknowledging what they observed accurately in the image."
    )
    incorrect_findings_note: str = Field(
        ...,
        description="Sentence about the findings the student reported that do not match the ground truth, without revealing any unidentified findings."
    )
    impression_note: str = Field(
        ...,
        description="Sentence clinical evaluation of the student's overall impressions, explaining why it was correct or incorrect based solely on the findings they identified and the ground truth impression."
    )

class XRayFinalReport(FinalReport):
    ground_truth_findings: list[str]
    ground_truth_findings_num: int
    correct_impression: str
    correct_findings: list[str]
    incorrect_findings: list[str]
    

class XRaySessionState(ChatSessionState):
    impression_attempts: list[Message] = Field(default_factory=list)

    image_url: str = ""
    radiology_case_id: str = ""

    # medgemma output
    ground_truth_findings: list[str] = Field(default_factory=list)
    impression: str = ""

    evaluation_sheet: EvaluationSheet = Field(default_factory=EvaluationSheet)

    @property
    def impression_attempts_num(self) -> int:
        return len(self.impression_attempts)

    @property
    def ground_truth_findings_num(self) -> int:
        return len(self.ground_truth_findings)

    @property
    def student_correct_findings(self) -> list[str]:
        return [f.finding for f in self.evaluation_sheet.correct_findings]
    
    @property
    def student_incorrect_findings(self) -> list[str]:
        return [inc.finding for inc in self.evaluation_sheet.incorrect_findings]

    @property
    def student_impressions(self) -> list[str]:
        return [imp.impression for imp in self.evaluation_sheet.impressions]
