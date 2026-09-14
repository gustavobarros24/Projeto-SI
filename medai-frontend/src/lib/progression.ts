// Mirrors backend/core/progression.py — keep thresholds in sync.

export const LEVEL_THRESHOLDS = [0, 100, 250, 450, 700]
export const MAX_LEVEL = LEVEL_THRESHOLDS.length

export interface LevelProgress {
  level: number
  isMax: boolean
  /** XP earned within the current level band. */
  xpIntoLevel: number
  /** XP span of the current level band (current_floor → next_threshold). */
  xpForLevel: number
  /** 0–100, fraction of the current band completed (100 at max level). */
  percent: number
}

export function progressForXp(xp: number): LevelProgress {
  let level = 1
  for (let i = 0; i < LEVEL_THRESHOLDS.length; i++) {
    if (xp >= LEVEL_THRESHOLDS[i]) level = i + 1
  }

  const currentFloor = LEVEL_THRESHOLDS[level - 1]
  const isMax = level >= MAX_LEVEL
  if (isMax) {
    return { level, isMax, xpIntoLevel: xp - currentFloor, xpForLevel: 0, percent: 100 }
  }

  const nextThreshold = LEVEL_THRESHOLDS[level]
  const xpForLevel = nextThreshold - currentFloor
  const xpIntoLevel = xp - currentFloor
  const percent = Math.max(0, Math.min(100, Math.round((xpIntoLevel / xpForLevel) * 100)))
  return { level, isMax, xpIntoLevel, xpForLevel, percent }
}
