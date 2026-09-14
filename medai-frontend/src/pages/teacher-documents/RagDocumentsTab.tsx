import { useEffect, useRef, useState } from "react"
import { FileText, Trash2, Upload } from "lucide-react"
import { useTranslation } from "react-i18next"

import {
  buildDocumentUrl,
  deleteDocument,
  listDocuments,
  uploadDocument,
  type DocumentMeta,
} from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const ACCEPTED = ".pdf,.docx,.txt,.md"

export function RagDocumentsTab() {
  const { t } = useTranslation()
  const [docs, setDocs] = useState<DocumentMeta[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  async function refresh() {
    setIsLoading(true)
    try {
      const list = await listDocuments()
      setDocs(list)
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
      const meta = await uploadDocument(file)
      setDocs((prev) => [meta, ...prev])
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsUploading(false)
      if (inputRef.current) inputRef.current.value = ""
    }
  }

  async function handleDelete(id: string) {
    setError(null)
    try {
      await deleteDocument(id)
      setDocs((prev) => prev.filter((d) => d.id !== id))
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">
            {t("teacher.documents.upload")}
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
            {t("teacher.documents.accepted")}
          </p>
          <UploadStatus isUploading={isUploading} />
          <UploadError error={error} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <FileText className="h-4 w-4" />
            {t("teacher.documents.list")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <DocumentsList docs={docs} isLoading={isLoading} onDelete={handleDelete} />
        </CardContent>
      </Card>
    </div>
  )
}

function UploadStatus({ isUploading }: { isUploading: boolean }) {
  const { t } = useTranslation()
  if (!isUploading) return null
  return (
    <p className="text-sm text-muted-foreground flex items-center gap-2">
      <Upload className="h-3.5 w-3.5 animate-pulse" />
      {t("teacher.documents.uploading")}
    </p>
  )
}

function UploadError({ error }: { error: string | null }) {
  if (!error) return null
  return <p className="text-sm text-destructive">{error}</p>
}

interface DocumentsListProps {
  docs: DocumentMeta[]
  isLoading: boolean
  onDelete: (id: string) => void
}

function DocumentsList({ docs, isLoading, onDelete }: DocumentsListProps) {
  const { t } = useTranslation()
  if (isLoading) {
    return <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
  }
  if (docs.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        {t("teacher.documents.empty")}
      </p>
    )
  }
  return (
    <ul className="divide-y">
      {docs.map((doc) => (
        <DocumentRow key={doc.id} doc={doc} onDelete={onDelete} />
      ))}
    </ul>
  )
}

function DocumentRow({ doc, onDelete }: { doc: DocumentMeta; onDelete: (id: string) => void }) {
  const { t } = useTranslation()
  return (
    <li className="flex items-center gap-3 py-2">
      <FileText className="h-4 w-4 text-muted-foreground shrink-0" />
      <a
        href={buildDocumentUrl(doc.id)}
        target="_blank"
        rel="noopener noreferrer"
        className="flex-1 truncate text-sm hover:underline"
      >
        {doc.filename}
      </a>
      <span className="text-xs text-muted-foreground hidden sm:inline">
        {new Date(doc.created_at).toLocaleString()}
      </span>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onDelete(doc.id)}
        aria-label={t("teacher.documents.delete_aria")}
      >
        <Trash2 className="h-4 w-4" />
      </Button>
    </li>
  )
}
