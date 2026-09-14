import { useEffect, useState } from "react"
import { RefreshCw } from "lucide-react"
import { useTranslation } from "react-i18next"

import {
  reExtractAnamnesisCase,
  updateAnamnesisCase,
  type AnamnesisCase,
  type AnamnesisCaseUpdate,
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

interface AnamnesisCaseEditorProps {
  open: boolean
  initialCase: AnamnesisCase | null
  onOpenChange: (open: boolean) => void
  onSaved: (updated: AnamnesisCase) => void
}

interface FormState {
  title: string
  description: string
  level: number
  patient_name: string
  patient_age: string
  patient_gender: string
  hidden_diagnosis: string
  symptoms_text: string
  patient_emotional_state: string
}

function caseToForm(c: AnamnesisCase): FormState {
  return {
    title: c.title ?? "",
    description: c.description ?? "",
    level: c.level ?? 1,
    patient_name: c.patient_name ?? "",
    patient_age: String(c.patient_age ?? ""),
    patient_gender: c.patient_gender ?? "",
    hidden_diagnosis: c.hidden_diagnosis ?? "",
    symptoms_text: (c.symptoms ?? []).join("\n"),
    patient_emotional_state: c.patient_emotional_state ?? "",
  }
}

function formToPayload(form: FormState): AnamnesisCaseUpdate {
  return {
    title: form.title.trim(),
    description: form.description.trim(),
    level: form.level,
    patient_name: form.patient_name.trim(),
    patient_age: Number.parseInt(form.patient_age || "0", 10) || 0,
    patient_gender: form.patient_gender.trim(),
    hidden_diagnosis: form.hidden_diagnosis.trim(),
    symptoms: form.symptoms_text
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean),
    patient_emotional_state: form.patient_emotional_state.trim(),
  }
}

export function AnamnesisCaseEditor({
  open,
  initialCase,
  onOpenChange,
  onSaved,
}: AnamnesisCaseEditorProps) {
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
  initialCase: AnamnesisCase
  onClose: () => void
  onSaved: (updated: AnamnesisCase) => void
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
      const payload: AnamnesisCaseUpdate = { ...formToPayload(form), status }
      if (status === "published") {
        if (!payload.title) {
          throw new Error(t("teacher.anamnesis_cases.editor.errors.title_required"))
        }
        if (!payload.description) {
          throw new Error(t("teacher.anamnesis_cases.editor.errors.description_required"))
        }
        if (!payload.hidden_diagnosis) {
          throw new Error(t("teacher.anamnesis_cases.editor.errors.diagnosis_required"))
        }
        if (!payload.symptoms || payload.symptoms.length === 0) {
          throw new Error(t("teacher.anamnesis_cases.editor.errors.symptoms_required"))
        }
      }
      const updated = await updateAnamnesisCase(initialCase.id, payload)
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
      const extracted = await reExtractAnamnesisCase(initialCase.id)
      setForm((prev) => ({
        ...prev,
        patient_name: extracted.patient_name,
        patient_age: String(extracted.patient_age),
        patient_gender: extracted.patient_gender,
        hidden_diagnosis: extracted.hidden_diagnosis,
        symptoms_text: extracted.symptoms.join("\n"),
        patient_emotional_state: extracted.patient_emotional_state,
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
          {t("teacher.anamnesis_cases.editor.title")}
        </DialogTitle>
        <DialogDescription>
          {t("teacher.anamnesis_cases.editor.description")}
        </DialogDescription>
      </DialogHeader>

      <div className="overflow-y-auto px-6 py-4 space-y-4">
        <SectionStudent t={t} form={form} update={update} />
        <SectionPatient t={t} form={form} update={update} />
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
            ? t("teacher.anamnesis_cases.editor.re_extracting")
            : t("teacher.anamnesis_cases.editor.re_extract")}
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
            ? t("teacher.anamnesis_cases.editor.saving")
            : t("teacher.anamnesis_cases.editor.save_draft")}
        </Button>
        <Button
          onClick={() => save("published")}
          disabled={savingStatus !== "idle"}
        >
          {savingStatus === "published"
            ? t("teacher.anamnesis_cases.editor.publishing")
            : t("teacher.anamnesis_cases.editor.publish")}
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
        {t("teacher.anamnesis_cases.editor.section_student")}
      </h3>
      <p className="text-xs text-muted-foreground">
        {t("teacher.anamnesis_cases.editor.section_student_hint")}
      </p>
      <div className="space-y-2">
        <Label htmlFor="ac-title">{t("teacher.anamnesis_cases.editor.field_title")}</Label>
        <Input
          id="ac-title"
          value={form.title}
          maxLength={255}
          onChange={(e) => update("title", e.target.value)}
          placeholder={t("teacher.anamnesis_cases.editor.placeholder_title")}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="ac-description">
          {t("teacher.anamnesis_cases.editor.field_description")}
        </Label>
        <textarea
          id="ac-description"
          value={form.description}
          maxLength={500}
          onChange={(e) => update("description", e.target.value)}
          placeholder={t("teacher.anamnesis_cases.editor.placeholder_description")}
          rows={2}
          className="block w-full rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="ac-level">{t("teacher.anamnesis_cases.editor.field_level")}</Label>
        <select
          id="ac-level"
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
          {t("teacher.anamnesis_cases.editor.field_level_hint")}
        </p>
      </div>
    </div>
  )
}

function SectionPatient({ t, form, update }: SectionProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">
        {t("teacher.anamnesis_cases.editor.section_patient")}
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="space-y-2">
          <Label htmlFor="ac-name">{t("teacher.anamnesis_cases.editor.field_name")}</Label>
          <Input
            id="ac-name"
            value={form.patient_name}
            onChange={(e) => update("patient_name", e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="ac-age">{t("teacher.anamnesis_cases.editor.field_age")}</Label>
          <Input
            id="ac-age"
            type="number"
            min={0}
            max={150}
            value={form.patient_age}
            onChange={(e) => update("patient_age", e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="ac-gender">{t("teacher.anamnesis_cases.editor.field_gender")}</Label>
          <Input
            id="ac-gender"
            value={form.patient_gender}
            onChange={(e) => update("patient_gender", e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="ac-emotional">
          {t("teacher.anamnesis_cases.editor.field_emotional")}
        </Label>
        <Input
          id="ac-emotional"
          value={form.patient_emotional_state}
          onChange={(e) => update("patient_emotional_state", e.target.value)}
        />
      </div>
    </div>
  )
}

function SectionClinical({ t, form, update }: SectionProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold">
        {t("teacher.anamnesis_cases.editor.section_clinical")}
      </h3>
      <div className="space-y-2">
        <Label htmlFor="ac-diagnosis">
          {t("teacher.anamnesis_cases.editor.field_diagnosis")}
        </Label>
        <textarea
          id="ac-diagnosis"
          value={form.hidden_diagnosis}
          onChange={(e) => update("hidden_diagnosis", e.target.value)}
          rows={2}
          className="block w-full rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="ac-symptoms">
          {t("teacher.anamnesis_cases.editor.field_symptoms")}
        </Label>
        <textarea
          id="ac-symptoms"
          value={form.symptoms_text}
          onChange={(e) => update("symptoms_text", e.target.value)}
          rows={6}
          placeholder={t("teacher.anamnesis_cases.editor.placeholder_symptoms")}
          className="block w-full rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
        />
        <p className="text-xs text-muted-foreground">
          {t("teacher.anamnesis_cases.editor.symptoms_hint")}
        </p>
      </div>
    </div>
  )
}

function FormError({ error }: { error: string | null }) {
  if (!error) return null
  return <p className="text-sm text-destructive">{error}</p>
}
