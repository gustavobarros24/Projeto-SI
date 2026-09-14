import { useEffect, useRef, useState } from "react"
import { Loader2, Pencil, ScanLine, Trash2 } from "lucide-react"
import { useTranslation } from "react-i18next"

import {
  buildRadiologyCaseFileUrl,
  deleteRadiologyCase,
  getRadiologyCase,
  listAllRadiologyCases,
  uploadRadiologyCase,
  type RadiologyCase,
  type RadiologyCaseAdminSummary,
} from "@/lib/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

import { RadiologyCaseEditor } from "./RadiologyCaseEditor"

const ACCEPTED = ".png,.jpg,.jpeg"

export function RadiologyCasesTab() {
  const { t } = useTranslation()
  const [cases, setCases] = useState<RadiologyCaseAdminSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<RadiologyCase | null>(null)
  const [editorOpen, setEditorOpen] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  async function refresh() {
    setIsLoading(true)
    try {
      const list = await listAllRadiologyCases()
      setCases(list)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setError(null)
    setIsUploading(true)
    try {
      const created = await uploadRadiologyCase(file)
      setCases((prev) => [toAdminSummary(created), ...prev])
      setEditing(created)
      setEditorOpen(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsUploading(false)
      if (inputRef.current) inputRef.current.value = ""
    }
  }

  async function handleEdit(id: string) {
    setError(null)
    try {
      const full = await getRadiologyCase(id)
      setEditing(full)
      setEditorOpen(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  async function handleDelete(id: string) {
    setError(null)
    try {
      await deleteRadiologyCase(id)
      setCases((prev) => prev.filter((c) => c.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  function handleSaved(updated: RadiologyCase) {
    setCases((prev) =>
      prev.map((c) => (c.id === updated.id ? toAdminSummary(updated) : c)),
    )
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">
            {t("teacher.radiology_cases.upload")}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED}
            onChange={handleFile}
            disabled={isUploading}
            className="block w-full text-sm file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-primary-foreground hover:file:cursor-pointer disabled:opacity-50"
          />
          <p className="text-xs text-muted-foreground">
            {t("teacher.radiology_cases.accepted")}
          </p>
          <UploadStatus isUploading={isUploading} />
          <FormError error={error} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <ScanLine className="h-4 w-4" />
            {t("teacher.radiology_cases.list")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <CasesList
            cases={cases}
            isLoading={isLoading}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </CardContent>
      </Card>

      <RadiologyCaseEditor
        open={editorOpen}
        initialCase={editing}
        onOpenChange={setEditorOpen}
        onSaved={handleSaved}
      />
    </div>
  )
}

function toAdminSummary(c: RadiologyCase): RadiologyCaseAdminSummary {
  return {
    id: c.id,
    title: c.title,
    level: c.level,
    status: c.status,
    original_filename: c.original_filename,
    uploaded_by: c.uploaded_by,
    created_at: c.created_at,
    updated_at: c.updated_at,
  }
}

function UploadStatus({ isUploading }: { isUploading: boolean }) {
  const { t } = useTranslation()
  if (!isUploading) return null
  return (
    <p className="text-sm text-muted-foreground flex items-center gap-2">
      <Loader2 className="h-3.5 w-3.5 animate-spin" />
      {t("teacher.radiology_cases.extracting")}
    </p>
  )
}

function FormError({ error }: { error: string | null }) {
  if (!error) return null
  return <p className="text-sm text-destructive">{error}</p>
}

interface CasesListProps {
  cases: RadiologyCaseAdminSummary[]
  isLoading: boolean
  onEdit: (id: string) => void
  onDelete: (id: string) => void
}

function CasesList({ cases, isLoading, onEdit, onDelete }: CasesListProps) {
  const { t } = useTranslation()
  if (isLoading) {
    return <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
  }
  if (cases.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        {t("teacher.radiology_cases.empty")}
      </p>
    )
  }
  return (
    <ul className="divide-y">
      {cases.map((c) => (
        <CaseRow key={c.id} caseData={c} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </ul>
  )
}

interface CaseRowProps {
  caseData: RadiologyCaseAdminSummary
  onEdit: (id: string) => void
  onDelete: (id: string) => void
}

function CaseRow({ caseData, onEdit, onDelete }: CaseRowProps) {
  const { t } = useTranslation()
  const title = caseData.title || t("teacher.radiology_cases.untitled")
  return (
    <li className="flex items-center gap-3 py-2.5">
      <img
        src={buildRadiologyCaseFileUrl(caseData.id)}
        alt={title}
        className="h-10 w-10 rounded object-cover bg-muted shrink-0"
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium truncate">{title}</span>
          <StatusBadge status={caseData.status} />
        </div>
        <p className="text-xs text-muted-foreground truncate">
          {caseData.original_filename}
        </p>
      </div>
      <span className="text-xs text-muted-foreground hidden sm:inline">
        {new Date(caseData.created_at).toLocaleDateString()}
      </span>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onEdit(caseData.id)}
        aria-label={t("teacher.radiology_cases.edit_aria")}
      >
        <Pencil className="h-4 w-4" />
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onDelete(caseData.id)}
        aria-label={t("teacher.radiology_cases.delete_aria")}
      >
        <Trash2 className="h-4 w-4" />
      </Button>
    </li>
  )
}

function StatusBadge({ status }: { status: "draft" | "published" }) {
  const { t } = useTranslation()
  if (status === "published") {
    return <Badge variant="default">{t("teacher.radiology_cases.status_published")}</Badge>
  }
  return <Badge variant="secondary">{t("teacher.radiology_cases.status_draft")}</Badge>
}
