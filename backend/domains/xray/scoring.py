from enum import Enum

class ImpressionAccuracy(int, Enum):
    EXACT_MATCH = 5
    CLINICALLY_EQUIVALENT = 4
    PARTIAL_MATCH = 3
    LIMITED_MATCH = 2
    MINIMAL_RELEVANCE = 1
    UNRELATED = 0

    @staticmethod
    def higher_of(new: "ImpressionAccuracy", old: "ImpressionAccuracy") -> "ImpressionAccuracy":
        return ImpressionAccuracy(max(new.value, old.value))

    @staticmethod
    def most_accurate(impressions: list["ImpressionAccuracy"]) -> "ImpressionAccuracy":
        if not impressions:
            return ImpressionAccuracy.UNRELATED
        return max(impressions, key=lambda i: i.value)

def get_impression_pts(impression: ImpressionAccuracy) -> int:
    if impression == ImpressionAccuracy.EXACT_MATCH or impression == ImpressionAccuracy.CLINICALLY_EQUIVALENT:
        return 10
    elif impression == ImpressionAccuracy.PARTIAL_MATCH:
        return 8
    elif impression == ImpressionAccuracy.LIMITED_MATCH:
        return 5
    elif impression == ImpressionAccuracy.MINIMAL_RELEVANCE:
        return 3
    elif impression == ImpressionAccuracy.UNRELATED:
        return 0
    else:
        return 0

def get_incorrect_findings_pts(incorrect_findings: int) -> int:
    if incorrect_findings <= 0:
        return 0
    elif incorrect_findings <= 3:
        return -5
    elif incorrect_findings <= 5:
        return -8
    elif incorrect_findings <= 8:
        return -12
    elif incorrect_findings <= 10:
        return -15
    else:
        return -20

def get_tries_pts(tries: int) -> int:
    if tries == 3:
        return 5
    elif tries == 2:
        return 8
    elif tries == 1:
        return 10
    else:
        return 0

def get_findings_pts(correct_found: int, total_expected: int) -> int:
    if total_expected <= 0:
        return 0
    ratio = correct_found / total_expected
    score = round(ratio * 80)
    return max(0, min(80, score))
