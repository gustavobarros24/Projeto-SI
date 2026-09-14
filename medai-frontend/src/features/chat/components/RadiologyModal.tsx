import { useEffect, useState } from "react"
import { Lock } from "lucide-react"
import { useTranslation } from "react-i18next"

import {
  buildRadiologyCaseFileUrl,
  listPublishedRadiologyCases,
  type RadiologyCaseSummary,
} from "@/lib/api"
import { useAuth } from "@/contexts/AuthContext"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface RadiologyModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSelect: (caseId: string) => void
}

type LoadState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "loaded"; cases: RadiologyCaseSummary[] }

export function RadiologyModal({ open, onOpenChange, onSelect }: RadiologyModalProps) {
  const { t } = useTranslation()
  const { user } = useAuth()
  const radiologyLevel = user?.radiology_level ?? 1
  const [load, setLoad] = useState<LoadState>({ kind: "loading" })
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    if (!open) return
    let cancelled = false
    listPublishedRadiologyCases()
      .then((cases) => {
        if (!cancelled) setLoad({ kind: "loaded", cases })
      })
      .catch((err) => {
        if (!cancelled) {
          setLoad({
            kind: "error",
            message: err instanceof Error ? err.message : String(err),
          })
        }
      })
    return () => {
      cancelled = true
    }
  }, [open])

  function handleConfirm() {
    if (selected) {
      onSelect(selected)
      setSelected(null)
    }
  }

  function handleOpenChange(value: boolean) {
    if (!value) {
      setSelected(null)
      setLoad({ kind: "loading" })
    }
    onOpenChange(value)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>{t("radiology_modal.title")}</DialogTitle>
          <DialogDescription>{t("radiology_modal.description")}</DialogDescription>
        </DialogHeader>

        <div className="px-6 py-4">
          <ModalBody
            load={load}
            selected={selected}
            radiologyLevel={radiologyLevel}
            onSelect={setSelected}
          />
        </div>

        <DialogFooter>
          <Button onClick={handleConfirm} disabled={!selected} className="w-full">
            {t("radiology_modal.confirm")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

interface ModalBodyProps {
  load: LoadState
  selected: string | null
  radiologyLevel: number
  onSelect: (id: string) => void
}

function ModalBody({ load, selected, radiologyLevel, onSelect }: ModalBodyProps) {
  const { t } = useTranslation()
  if (load.kind === "loading") {
    return <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
  }
  if (load.kind === "error") {
    return <p className="text-sm text-destructive">{load.message}</p>
  }
  if (load.cases.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">{t("radiology_modal.empty")}</p>
    )
  }
  return (
    <ul className="grid grid-cols-2 gap-3 max-h-[60vh] overflow-y-auto">
      {load.cases.map((c) => (
        <CaseOption
          key={c.id}
          caseData={c}
          isSelected={c.id === selected}
          isLocked={c.level > radiologyLevel}
          onSelect={() => onSelect(c.id)}
        />
      ))}
    </ul>
  )
}

interface CaseOptionProps {
  caseData: RadiologyCaseSummary
  isSelected: boolean
  isLocked: boolean
  onSelect: () => void
}

function CaseOption({ caseData, isSelected, isLocked, onSelect }: CaseOptionProps) {
  if (isLocked) {
    return <LockedCaseOption caseData={caseData} />
  }
  return (
    <SelectableCaseOption
      caseData={caseData}
      isSelected={isSelected}
      onSelect={onSelect}
    />
  )
}

interface SelectableCaseOptionProps {
  caseData: RadiologyCaseSummary
  isSelected: boolean
  onSelect: () => void
}

function SelectableCaseOption({ caseData, isSelected, onSelect }: SelectableCaseOptionProps) {
  const { t } = useTranslation()
  const title = caseData.title || t("radiology_modal.untitled")
  return (
    <li>
      <button
        type="button"
        onClick={onSelect}
        className={selectionButtonClasses(isSelected)}
      >
        <img
          src={buildRadiologyCaseFileUrl(caseData.id)}
          alt={title}
          className="h-32 w-full rounded-md object-cover bg-muted"
        />
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-medium truncate">{title}</p>
          <Badge variant="secondary" className="shrink-0">
            {t("radiology_modal.required_level", { level: caseData.level })}
          </Badge>
        </div>
      </button>
    </li>
  )
}

function LockedCaseOption({ caseData }: { caseData: RadiologyCaseSummary }) {
  const { t } = useTranslation()
  const title = caseData.title || t("radiology_modal.untitled")
  return (
    <li>
      <div
        className="flex flex-col gap-2 rounded-lg border-2 border-muted bg-muted/30 p-2 opacity-70 cursor-not-allowed"
        aria-disabled="true"
      >
        <div className="relative h-32 w-full">
          <img
            src={buildRadiologyCaseFileUrl(caseData.id)}
            alt={title}
            className="h-32 w-full rounded-md object-cover bg-muted grayscale"
          />
          <div className="absolute inset-0 flex items-center justify-center">
            <Lock className="h-6 w-6 text-muted-foreground" />
          </div>
        </div>
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-medium truncate">{title}</p>
          <Badge variant="outline" className="shrink-0">
            {t("radiology_modal.required_level", { level: caseData.level })}
          </Badge>
        </div>
      </div>
    </li>
  )
}

function selectionButtonClasses(isSelected: boolean): string {
  const base =
    "w-full flex flex-col gap-2 rounded-lg border-2 p-2 transition-colors cursor-pointer text-left"
  if (isSelected) {
    return `${base} border-primary ring-2 ring-primary/20 bg-primary/5`
  }
  return `${base} border-muted hover:border-muted-foreground/30`
}
