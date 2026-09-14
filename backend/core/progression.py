"""Student progression: per-module level derived from accumulated XP.

XP is the session score (FinalReport.total_points, 0-100) summed across completed
sessions. Levels run 1-5; LEVEL_THRESHOLDS[i] is the total XP required to reach
level i+1.
"""

LEVEL_THRESHOLDS = [0, 100, 250, 450, 700]
MAX_LEVEL = len(LEVEL_THRESHOLDS)


def level_for_xp(xp: int) -> int:
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
    return level


def progress_for_xp(xp: int) -> dict:
    """Shape for a level + XP progress bar.

    current_floor / next_threshold bound the current level; next_threshold is None
    at the max level.
    """
    level = level_for_xp(xp)
    current_floor = LEVEL_THRESHOLDS[level - 1]
    next_threshold = LEVEL_THRESHOLDS[level] if level < MAX_LEVEL else None
    return {
        "level": level,
        "xp": xp,
        "current_floor": current_floor,
        "next_threshold": next_threshold,
    }
