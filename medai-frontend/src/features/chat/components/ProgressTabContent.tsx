import { TargetIcon } from "lucide-react"
import type { SessionInfo } from "@/lib/api"
import { RadiologyProgress } from "./RadiologyProgress"
import { AnamnesisProgress } from "./AnamnesisProgress"
import { useTranslation } from "react-i18next"

interface ProgressTabContentProps {
  session: SessionInfo | null
}

export function ProgressTabContent({ session }: ProgressTabContentProps) {
  const { t } = useTranslation()

  if (!session) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <TargetIcon className="size-10 mb-2 opacity-50" />
        <p className="text-sm">{t("progress.start_session")}</p>
      </div>
    )
  }

  if (session.module === "radiology") {
    return <RadiologyProgress session={session} />
  }

  return <AnamnesisProgress session={session} />
}
