import type { Message } from "@/lib/api"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { useTranslation } from "react-i18next"
import Markdown from "react-markdown"
import { SourceDocumentButtons } from "@/components/SourceDocumentButtons"
import { AudioPlayer } from "@/components/AudioPlayer"

export function MessageBubble({ role, content, source, source_documents, audio_id }: Message) {
  const { t } = useTranslation()

  const isHuman = role === "human"
  const isPatient = source === "patient"
  const isTutor = source === "tutor"
  const isResponder = source === "responder"
  const isDiagnosis = source === "diagnosis"

  function getLabel() {
    switch (source) {
      case "patient":      return t("message.labels.patient")
      case "tutor":        return t("message.labels.tutor")
      case "presentation": return t("message.labels.presentation")
      case "responder":    return t("message.labels.responder")
      case "diagnosis":    return t("message.labels.diagnosis")
      default:             return null
    }
  }

  function getAvatarText() {
    if (isHuman)    return t("message.avatars.human")
    if (isPatient)  return "P"
    if (isTutor)    return "T"
    if (isResponder) return "R"
    return "AI"
  }

  const label = getLabel()
  const avatarText = getAvatarText()

  return (
    <div
      className={cn("flex items-end gap-2 mb-4", isHuman && "flex-row-reverse")}
    >
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback
          className={cn(
            "text-xs",
            isDiagnosis
              ? "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300"
              : isHuman
                ? "bg-primary text-primary-foreground"
                : isPatient
                  ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300"
                  : "bg-muted text-muted-foreground",
          )}
        >
          {avatarText}
        </AvatarFallback>
      </Avatar>
      <div className="flex flex-col gap-1 max-w-[75%]">
        <div
          className={cn(
            "rounded-lg px-4 py-2 text-sm",
            isHuman && "whitespace-pre-wrap",
            isDiagnosis
              ? "bg-amber-50 text-foreground border border-amber-200 self-end dark:bg-amber-950 dark:border-amber-800"
              : isHuman
                ? "bg-primary text-primary-foreground self-end"
                : isPatient
                  ? "bg-blue-50 text-foreground dark:bg-blue-950"
                  : "bg-muted text-foreground",
          )}
        >
          <MessageBody isHuman={isHuman} content={content} audioId={audio_id} />
          <SourceDocumentButtons sources={source_documents} />
        </div>
        {label && (
          <span className="text-xs text-muted-foreground px-1">{label}</span>
        )}
      </div>
    </div>
  )
}

function MessageBody({ isHuman, content, audioId }: { isHuman: boolean; content: string; audioId?: string }) {
  if (audioId) {
    return (
      <>
        <AudioPlayer audioId={audioId} />
        <p className="mt-1 text-xs text-muted-foreground whitespace-pre-wrap">{content}</p>
      </>
    )
  }
  if (isHuman) return <>{content}</>
  return (
    <div className="prose prose-sm dark:prose-invert max-w-none">
      <Markdown>{content}</Markdown>
    </div>
  )
}
