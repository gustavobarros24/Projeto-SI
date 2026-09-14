import {
  useModelsHealth,
  type ModelsHealthStatus,
} from "@/hooks/use-models-health"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import { cn } from "@/lib/utils"
import { Badge } from "./ui/badge"
import { useTranslation } from "react-i18next"

const statusBadgeVariants = {
  ok: "default",
  error: "destructive",
  loading: "outline",
} as const

export function ModelsStatusPill() {
  const { status, message } = useModelsHealth()
  const { t } = useTranslation()

  const label = labelFor(status, t)

  return (
    <TooltipProvider delay={150}>
      <Tooltip>
        <TooltipTrigger aria-label={t("models.status_aria", { status: label })}>
          <Badge variant={statusBadgeVariants[status]}>
            <StatusDot status={status} />
            <span>{label}</span>
          </Badge>
        </TooltipTrigger>
        <TooltipContent>{message}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}

function StatusDot({ status }: { status: ModelsHealthStatus }) {
  return (
    <span
      className={cn(
        "size-2 rounded-full",
        status === "ok" && "bg-emerald-500",
        status === "error" && "bg-red-500",
        status === "loading" && "bg-muted-foreground animate-pulse",
      )}
    />
  )
}

function labelFor(status: ModelsHealthStatus, t: (key: string) => string): string {
  if (status === "ok") return t("models.online")
  if (status === "error") return t("models.unavailable")
  return t("models.checking")
}
