import { AlertTriangle } from "lucide-react"
import { useModelsHealth } from "@/hooks/use-models-health"
import { useTranslation } from "react-i18next"

export function ModelsStatusBanner() {
  const { status, message } = useModelsHealth()
  const { t } = useTranslation()

  if (status !== "error") return null

  return (
    <div className="border-t border-destructive/30 bg-destructive/10 px-4 py-2">
      <div className="max-w-3xl mx-auto flex items-start gap-2 text-sm text-destructive">
        <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0" />
        <div>
          <p className="font-medium">{t("models.unavailable")}</p>
          <p className="text-destructive/80">{message}</p>
        </div>
      </div>
    </div>
  )
}
