import { useEffect, useState } from "react"
import { RefreshCw } from "lucide-react"
import { useTranslation } from "react-i18next"

import {
  buildRadiologyCaseFileUrl,
  reExtractRadiologyCase,
  updateRadiologyCase,
  type RadiologyCase,
  type RadiologyCaseUpdate,
} from "@/lib/api"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface RadiologyCaseEditorProps {
  open: boolean
  initialCase: RadiologyCase | null
  onOpenChange: (open: boolean) => void
  onSaved: (updated: RadiologyCase) => void
}

interface FormState {
  title: string
  level: number
  findings_text: string
  impression: string
}

function caseToForm(c: RadiologyCase): FormState {
  return {
    title: c.title ?? "",
    level: c.level ?? 1,
    findings_text: (c.ground_findings ?? []).join("\n"),
    impression: c.impression ?? "",
  }
}

function formToPayload(form: FormState): RadiologyCaseUpdate {
  return {
    title: form.title.trim(),
    level: form.level,
    ground_findings: form.findings_text
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean),
    impression: form.impression.trim(),
  }
}

export function RadiologyCaseEditor({
  open,
  initialCase,
  onOpenChange,
  onSaved,
}: RadiologyCaseEditorProps) {
  if (!initialCase) return null
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <EditorBody
          initialCase={initialCase}
          onClose={() => onOpenChange(false)}
          onSaved={onSaved}
        />
      </DialogContent>
    </Dialog>
  )
}

interface EditorBodyProps {
  initialCase: RadiologyCase
  onClose: () => void
  onSaved: (updated: RadiologyCase) => void
}

function EditorBody({ initialCase, onClose, onSaved }: EditorBodyProps) {
  const { t } = useTranslation()
  const [form, setForm] = useState<FormState>(() => caseToForm(initialCase))
  const [error, setError] = useState<string | null>(null)
  const [savingStatus, setSavingStatus] = useState<"idle" | "draft" | "published">("idle")
  const [isReExtracting, setIsReExtracting] = useState(false)

  useEffect(() => {
    setForm(caseToForm(initialCase))
    setError(null)
  }, [initialCase])

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function save(status: "draft" | "published") {
    setError(null)
    setSavingStatus(status)
    try {
      const payload: RadiologyCaseUpdate = { ...formToPayload(form), status }
      if (status === "published") {
        if (!payload.title) {
          throw new Error(t("teacher.radiology_cases.editor.errors.title_required"))
        }
        if (!payload.ground_findings || payload.ground_findings.length === 0) {
          throw new Error(t("teacher.radiology_cases.editor.errors.findings_required"))
        }
        if (!payload.impression) {
          throw new Error(t("teacher.radiology_cases.editor.errors.impression_required"))
        }
      }
      const updated = await updateRadiologyCase(initialCase.id, payload)
      onSaved(updated)
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setSavingStatus("idle")
    }
  }

  async function handleReExtract() {
    setError(null)
    setIsReExtracting(true)
    try {
      const extracted = await reExtractRadiologyCase(initialCase.id)
      setForm((prev) => ({
        ...prev,
        findings_text: extracted.ground_findings.join("\n"),
        impression: extracted.impression,
      }))
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsReExtracting(false)
    }
  }

  return (
    <>
      <DialogHeader>
        <DialogTitle>
          {t("teacher.radiology_cases.editor.title")}
        </DialogTitle>
        <DialogDescription>
          {t("teacher.radiology_cases.editor.description")}
        </DialogDescription>
      </DialogHeader>

      <div className="overflow-y-auto px-6 py-4 space-y-4">
        <img
          src={buildRadiologyCaseFileUrl(initialCase.id)}
          alt={form.title || t("teacher.radiology_cases.untitled")}
          className="max-h-64 w-full rounded-lg object-contain bg-muted"
        />

        <SectionStudent t={t} form={form} update={update} />
        <SectionClinical t={t} form={form} update={update} />

        <FormError error={error} />

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleReExtract}
          disabled={isReExtracting}
          className="gap-2"
        >
          <RefreshCw className={isReExtracting ? "h-4 w-4 animate-spin" : "h-4 w-4"} />
          {isReExtracting
            ? t("teacher.radiology_cases.editor.re_extracting")
            : t("teacher.radiology_cases.editor.re_extract")}
        </Button>
      </div>

      <DialogFooter>
        <Button variant="ghost" onClick={onClose} disabled={savingStatus !== "idle"}>
          {t("common.cancel")}
        </Button>
        <Button
          variant="outline"
          onClick={() => save("draft")}
          disabled={savingStatus !== "idle"}
        >
          {savingStatus === "draft"
            ? t("teacher.radiology_cases.editor.saving")
            : t("teacher.radiology_cases.editor.save_draft")}
        </Button>
        <Button
          onClick={() => save("published")}
          disabled={savingStatus !== "idle"}
        >
          {savingStatus === "published"
            ? t("teacher.radiology_cases.editor.publishing")
            : t("teacher.radiology_cases.editor.publish")}
        </Button>
      </DialogFooter>
    </>
  )
}

interface SectionProps {
  t: ReturnType<typeof useTranslation>["t"]
  form: FormState
  update: <K extends keyof FormState>(key: K, value: FormState[K]) => void
}

function SectionStudent({ t, form, update }: SectionProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">
        {t("teacher.radiology_cases.editor.section_student")}
      </h3>
      <div className="space-y-2">
        <Label htmlFor="rc-title">{t("teacher.radiology_cases.editor.field_title")}</Label>
        <Input
          id="rc-title"
          value={form.title}
          maxLength={255}
          onChange={(e) => update("title", e.target.value)}
          placeholder={t("teacher.radiology_cases.editor.placeholder_title")}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="rc-level">{t("teacher.radiology_cases.editor.field_level")}</Label>
        <select
          id="rc-level"
          value={form.level}
          onChange={(e) => update("level", Number(e.target.value))}
          className="block w-full rounded-lg border border-input bg-transparent px-2.5 py-1.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        >
          {[1, 2, 3, 4, 5].map((n) => (
            <option key={n} value={n}>
              {n}
            </option>
          ))}
        </select>
        <p className="text-xs text-muted-foreground">
          {t("teacher.radiology_cases.editor.field_level_hint")}
        </p>
      </div>
    </div>
  )
}

function SectionClinical({ t, form, update }: SectionProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">
        {t("teacher.radiology_cases.editor.section_clinical")}
      </h3>
      <div className="space-y-2">
        <Label htmlFor="rc-findings">
          {t("teacher.radiology_cases.editor.field_findings")}
        </Label>
        <textarea
          id="rc-findings"
          value={form.findings_text}
          onChange={(e) => update("findings_text", e.target.value)}
          rows={6}
          placeholder={t("teacher.radiology_cases.editor.placeholder_findings")}
          className="block w-full rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        />
        <p className="text-xs text-muted-foreground">
          {t("teacher.radiology_cases.editor.field_findings_hint")}
        </p>
      </div>
      <div className="space-y-2">
        <Label htmlFor="rc-impression">
          {t("teacher.radiology_cases.editor.field_impression")}
        </Label>
        <textarea
          id="rc-impression"
          value={form.impression}
          onChange={(e) => update("impression", e.target.value)}
          rows={2}
          placeholder={t("teacher.radiology_cases.editor.placeholder_impression")}
          className="block w-full rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        />
      </div>
    </div>
  )
}

function FormError({ error }: { error: string | null }) {
  if (!error) return null
  return <p className="text-sm text-destructive">{error}</p>
}
