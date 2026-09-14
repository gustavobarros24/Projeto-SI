import type { XraySession } from "@/lib/api"
import { StatCard } from "./StatCard"
import {
  CircleXIcon,
  FlameIcon,
  MessageCircleQuestionIcon,
  SearchIcon,
} from "lucide-react"
import { useTranslation } from "react-i18next"

interface RadiologyProgressProps {
  session: XraySession
}

export function RadiologyProgress({ session }: RadiologyProgressProps) {
  const { t } = useTranslation()

  const studentFindings = session.student_findings ?? []
  const groundTruthFindings = session.ground_truth_findings ?? []
  const incorrectFindings = session.incorrect_findings ?? []

  const foundList = studentFindings.map((finding) => `- ${finding}`)
  const missingCount = Math.max(
    0,
    groundTruthFindings.length - studentFindings.length,
  )
  const missingFindings = Array.from({ length: missingCount }, () => "??")
  const findingsList = [...foundList, ...missingFindings]

  const wrongFindingsList = incorrectFindings.map((finding) => `- ${finding}`)

  const correctProgress =
    groundTruthFindings.length > 0
      ? (studentFindings.length / groundTruthFindings.length) * 100
      : 0

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
        {t("progress.title")}
      </h3>

      <StatCard
        icon={<SearchIcon className="size-4" />}
        label={t("progress.radiology.correct_findings")}
        value={`${studentFindings.length} / ${groundTruthFindings.length}`}
        progress={correctProgress}
        list={findingsList}
      />

      <StatCard
        icon={<CircleXIcon className="size-4" />}
        label={t("progress.radiology.incorrect_findings")}
        value={String(incorrectFindings.length)}
        list={wrongFindingsList}
      />

      <StatCard
        icon={<FlameIcon className="size-4" />}
        label={t("progress.radiology.consecutive_errors")}
        value={String(session.consecutive_error_count ?? 0)}
      />

      <StatCard
        icon={<MessageCircleQuestionIcon className="size-4" />}
        label={t("progress.radiology.turn")}
        value={String(session.turn_count)}
      />
    </div>
  )
}
