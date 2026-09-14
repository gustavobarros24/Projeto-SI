from enum import Enum

class DiagnosisAccuracy(int, Enum):
    EXACT = 4
    SAME_DISEASE_GROUP = 3
    RELATED = 2
    UNRELATED = 1

    @staticmethod
    def higher_of(new: "DiagnosisAccuracy", old: "DiagnosisAccuracy") -> "DiagnosisAccuracy":
        return DiagnosisAccuracy(max(new.value, old.value))

    @staticmethod
    def most_accurate(diagnosis: list["DiagnosisAccuracy"]) -> "DiagnosisAccuracy":
        if not diagnosis:
            return DiagnosisAccuracy.UNRELATED
        return DiagnosisAccuracy(max(diagnosis, key=lambda d: d.value))       


def get_diagnosis_points(diagnosis: DiagnosisAccuracy) -> int:
    if diagnosis == DiagnosisAccuracy.EXACT:
        return 70
    elif diagnosis == DiagnosisAccuracy.SAME_DISEASE_GROUP:
        return 50
    elif diagnosis == DiagnosisAccuracy.RELATED:
        return 30
    elif diagnosis == DiagnosisAccuracy.UNRELATED:
        return 0
    else:
        return 0

def get_tries_pts(tries: int) -> int:
    if tries == 3:
        return 5
    elif tries == 2:
        return 10
    elif tries == 1:
        return 20
    else:
        return 0

def get_symptom_match_pts(found_symptoms: int, all_symptoms: int) -> int: 
    if all_symptoms <= 0:
        return 0
    ratio = found_symptoms / all_symptoms
    score = round(ratio * 10)
    return max(0, min(10, score))
