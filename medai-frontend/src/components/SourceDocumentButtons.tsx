import { FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { buildDocumentUrl, type SourceDocument } from "@/lib/api"
import { useTranslation } from "react-i18next"

export function SourceDocumentButtons({ sources }: { sources?: SourceDocument[] }) {
  const { t } = useTranslation()
  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-3 pt-2 border-t border-foreground/10 flex flex-col gap-1">
      <span className="text-[10px] uppercase tracking-wide text-muted-foreground">
        {t("message.sources")}
      </span>
      <div className="flex flex-wrap gap-1">
        {sources.map((doc) => (
          <a
            key={doc.id}
            href={buildDocumentUrl(doc.id)}
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button variant="outline" size="sm" className="gap-1.5 h-7 px-2 text-xs">
              <FileText className="h-3.5 w-3.5" />
              <span className="truncate max-w-[180px]">{doc.title}</span>
            </Button>
          </a>
        ))}
      </div>
    </div>
  )
}
