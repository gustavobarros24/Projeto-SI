import { useEffect, useState } from "react"
import { Lock, Stethoscope } from "lucide-react"
import { useTranslation } from "react-i18next"

import {
  listPublishedAnamnesisCases,
  type AnamnesisCaseSummary,
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

interface AnamnesisModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSelect: (caseId: string) => void
}

type LoadState =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "loaded"; cases: AnamnesisCaseSummary[] }

export function AnamnesisModal({ open, onOpenChange, onSelect }: AnamnesisModalProps) {
  const { t } = useTranslation()
  const { user } = useAuth()
  const anamnesisLevel = user?.anamnesis_level ?? 1
  const [load, setLoad] = useState<LoadState>({ kind: "loading" })
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    if (!open) return
    let cancelled = false
    listPublishedAnamnesisCases()
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
          <DialogTitle>{t("anamnesis_modal.title")}</DialogTitle>
          <DialogDescription>{t("anamnesis_modal.description")}</DialogDescription>
        </DialogHeader>

        <div className="px-6 py-4">
          <ModalBody
            load={load}
            selected={selected}
            anamnesisLevel={anamnesisLevel}
            onSelect={setSelected}
          />
        </div>

        <DialogFooter>
          <Button
            onClick={handleConfirm}
            disabled={!selected}
            className="w-full"
          >
            {t("anamnesis_modal.confirm")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

interface ModalBodyProps {
  load: LoadState
  selected: string | null
  anamnesisLevel: number
  onSelect: (id: string) => void
}

function ModalBody({ load, selected, anamnesisLevel, onSelect }: ModalBodyProps) {
  const { t } = useTranslation()
  if (load.kind === "loading") {
    return <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
  }
  if (load.kind === "error") {
    return <p className="text-sm text-destructive">{load.message}</p>
  }
  if (load.cases.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        {t("anamnesis_modal.empty")}
      </p>
    )
  }
  return (
    <ul className="flex flex-col gap-2 max-h-[60vh] overflow-y-auto">
      {load.cases.map((c) => (
        <CaseOption
          key={c.id}
          caseData={c}
          isSelected={c.id === selected}
          isLocked={c.level > anamnesisLevel}
          onSelect={() => onSelect(c.id)}
        />
      ))}
    </ul>
  )
}

interface CaseOptionProps {
  caseData: AnamnesisCaseSummary
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
  caseData: AnamnesisCaseSummary
  isSelected: boolean
  onSelect: () => void
}

function SelectableCaseOption({ caseData, isSelected, onSelect }: SelectableCaseOptionProps) {
  const { t } = useTranslation()
  const title = caseData.title || t("anamnesis_modal.untitled")
  return (
    <li>
      <button
        type="button"
        onClick={onSelect}
        className={selectionButtonClasses(isSelected)}
      >
        <Stethoscope className="h-5 w-5 mt-0.5 text-muted-foreground shrink-0" />
        <div className="flex-1 min-w-0 text-left">
          <p className="text-sm font-medium truncate">{title}</p>
          <p className="text-xs text-muted-foreground line-clamp-2">
            {caseData.description}
          </p>
        </div>
        <Badge variant="secondary" className="shrink-0">
          {t("anamnesis_modal.required_level", { level: caseData.level })}
        </Badge>
      </button>
    </li>
  )
}

function LockedCaseOption({ caseData }: { caseData: AnamnesisCaseSummary }) {
  const { t } = useTranslation()
  const title = caseData.title || t("anamnesis_modal.untitled")
  return (
    <li>
      <div
        className="w-full flex items-start gap-3 rounded-lg border-2 border-muted bg-muted/30 px-3 py-2.5 text-left opacity-70 cursor-not-allowed"
        aria-disabled="true"
      >
        <Lock className="h-5 w-5 mt-0.5 text-muted-foreground shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{title}</p>
          <p className="text-xs text-muted-foreground">
            {t("anamnesis_modal.locked", { level: caseData.level })}
          </p>
        </div>
        <Badge variant="outline" className="shrink-0">
          {t("anamnesis_modal.required_level", { level: caseData.level })}
        </Badge>
      </div>
    </li>
  )
}

function selectionButtonClasses(isSelected: boolean): string {
  const base =
    "w-full flex items-start gap-3 rounded-lg border-2 px-3 py-2.5 transition-colors cursor-pointer text-left"
  if (isSelected) {
    return `${base} border-primary ring-2 ring-primary/20 bg-primary/5`
  }
  return `${base} border-muted hover:border-muted-foreground/30`
}
