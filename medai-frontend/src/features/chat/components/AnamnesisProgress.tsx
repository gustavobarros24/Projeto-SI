import {
  CircleAlertIcon,
  EarIcon,
  FlameIcon,
  MessageCircleQuestionIcon,
} from "lucide-react"
import type { AnamnesisSession } from "@/lib/api"
import { StatCard } from "./StatCard"
import { useTranslation } from "react-i18next"

interface AnamnesisProgressProps {
  session: AnamnesisSession
}

export function AnamnesisProgress({ session }: AnamnesisProgressProps) {
  const { t } = useTranslation()

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
        {t("progress.title")}
      </h3>

      <StatCard
        icon={<EarIcon className="size-4" />}
        label={t("progress.anamnesis.symptoms_revealed")}
        value={String(session.covered_symptoms?.length ?? 0)}
      />
      <StatCard
        icon={<MessageCircleQuestionIcon className="size-4" />}
        label={t("progress.anamnesis.questions_asked")}
        value={String(session.questions_asked?.length ?? 0)}
      />
      <StatCard
        icon={<CircleAlertIcon className="size-4" />}
        label={t("progress.anamnesis.consecutive_irrelevant")}
        value={String(session.consecutive_irrelevant_count ?? 0)}
      />
      <StatCard
        icon={<FlameIcon className="size-4" />}
        label={t("progress.anamnesis.turn")}
        value={String(session.turn_count)}
      />
    </div>
  )
}
