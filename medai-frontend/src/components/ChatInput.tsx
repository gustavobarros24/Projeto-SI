import { useState, type FormEvent, type KeyboardEvent } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AlertDialog, AlertDialogTrigger, AlertDialogClose, AlertDialogContent, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter } from "@/components/ui/alert-dialog"
import { Send, Paperclip, Stethoscope, Flag, FileText } from "lucide-react"
import { useTranslation } from "react-i18next"
import { MicButton } from "@/components/MicButton"

interface ChatInputProps {
  onSend: (message: string) => void
  onSendVoice?: (blob: Blob) => Promise<void>
  onVoiceError?: (message: string) => void
  onDiagnosis?: (diagnosis: string) => void
  onGiveUp?: () => void
  onViewReport?: () => void
  diagnosisAttempts?: { remaining: number; total: number }
  disabled: boolean
  casePresented: boolean
}

export function ChatInput({ onSend, onSendVoice, onVoiceError, onDiagnosis, onGiveUp, onViewReport, diagnosisAttempts, disabled, casePresented }: ChatInputProps) {
  const { t } = useTranslation()
  const [text, setText] = useState("")
  const [isEvaluatorMode, setIsEvaluatorMode] = useState(false)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = text.trim()
    if (!trimmed || disabled) return

    if (isEvaluatorMode && onDiagnosis) {
      onDiagnosis(trimmed)
      setIsEvaluatorMode(false)
    } else {
      onSend(trimmed)
    }
    setText("")
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  function toggleEvaluatorMode() {
    setIsEvaluatorMode((prev) => !prev)
    setText("")
  }

  function handleConfirmGiveUp() {
    setIsEvaluatorMode(false)
    setText("")
    onGiveUp?.()
  }

  const diagnosisTitle = !casePresented
    ? t("chat.input.await_case")
    : isEvaluatorMode
      ? t("chat.input.cancel_diagnosis")
      : t("chat.input.submit_diagnosis")

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t bg-background px-4 py-3"
    >
      <div className="max-w-3xl mx-auto flex items-center gap-2">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          disabled
          title={t("chat.input.attachment_soon")}
        >
          <Paperclip className="h-4 w-4" />
        </Button>
        <MicButton
          onRecorded={onSendVoice}
          onError={onVoiceError}
          disabled={disabled || !casePresented}
        />
        <Button
          type="button"
          variant={isEvaluatorMode ? "default" : "outline"}
          onClick={toggleEvaluatorMode}
          title={diagnosisTitle}
          className="shrink-0 gap-1.5"
          disabled={disabled || !casePresented}
        >
          <Stethoscope className="h-4 w-4" />
          {isEvaluatorMode && diagnosisAttempts && (
            <span className="text-xs opacity-70">
              {diagnosisAttempts.remaining}/{diagnosisAttempts.total}
            </span>
          )}
        </Button>
        {isEvaluatorMode && (
          <AlertDialog>
            <AlertDialogTrigger
              render={
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  disabled={disabled}
                  title={t("chat.input.give_up")}
                  className="shrink-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                >
                  <Flag className="h-4 w-4" />
                </Button>
              }
            />
            <AlertDialogContent>
              <AlertDialogTitle>{t("chat.input.give_up_dialog.title")}</AlertDialogTitle>
              <AlertDialogDescription>
                {t("chat.input.give_up_dialog.description")}
              </AlertDialogDescription>
              <AlertDialogFooter>
                <AlertDialogClose render={<Button type="button" variant="outline">{t("common.cancel")}</Button>} />
                <AlertDialogClose render={<Button type="button" variant="destructive" onClick={handleConfirmGiveUp}>{t("chat.input.give_up")}</Button>} />
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        )}
        <Input
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            isEvaluatorMode
              ? t("chat.input.placeholder_diagnosis")
              : t("chat.input.placeholder_message")
          }
          disabled={disabled}
          className={`flex-1 transition-colors ${isEvaluatorMode ? "border-primary ring-1 ring-primary" : ""}`}
        />
        <Button type="submit" size="icon" disabled={disabled || !text.trim()}>
          <Send className="h-4 w-4" />
        </Button>
        {onViewReport && (
          <Button type="button" variant="outline" size="sm" onClick={onViewReport} className="gap-1.5 shrink-0">
            <FileText className="h-4 w-4" />
            {t("chat.input.view_report")}
          </Button>
        )}
      </div>
    </form>
  )
}
