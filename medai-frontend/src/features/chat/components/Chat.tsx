import { useState, useEffect } from "react"
import { useParams } from "react-router"
import {
  getChat,
  sendMessage,
  sendVoiceMessage,
  submitDiagnosis,
  giveUp,
  type Message,
  type SessionInfo,
} from "@/lib/api"
import { MessageList } from "@/components/MessageList"
import { ChatInput } from "@/components/ChatInput"
import { FinalReportPanel } from "@/components/FinalReportPanel"
import { XRayFinalReportPanel } from "@/components/XRayFinalReportPanel"
import type { XRayFinalReport } from "@/lib/api"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { FileText } from "lucide-react"
import { useSession } from "@/contexts/SessionContext"
import { useAuth } from "@/contexts/AuthContext"
import { useModelsHealth } from "@/hooks/use-models-health"
import { ModelsStatusBanner } from "@/components/ModelsStatusBanner"
import { useTranslation } from "react-i18next"

type LocalDiagnosis = { msg: Message; insertAfterIndex: number }

function mergeWithDiagnoses(
  serverMessages: Message[],
  diagnoses: LocalDiagnosis[],
): Message[] {
  if (diagnoses.length === 0) return serverMessages
  const result = [...serverMessages]
  const sorted = [...diagnoses].sort(
    (a, b) => b.insertAfterIndex - a.insertAfterIndex,
  )
  for (const { msg, insertAfterIndex } of sorted) {
    result.splice(insertAfterIndex + 1, 0, msg)
  }
  return result
}

export function Chat() {
  const { threadId } = useParams<{ threadId: string }>()
  const { setSession } = useSession()
  const { refreshUser } = useAuth()
  const { status: modelsStatus } = useModelsHealth()
  const { t, i18n } = useTranslation()

  const [messages, setMessages] = useState<Message[]>([])
  const [localDiagnoses, setLocalDiagnoses] = useState<LocalDiagnosis[]>([])
  const [localSession, setLocalSession] = useState<SessionInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reportOpen, setReportOpen] = useState(false)

  useEffect(() => {
    const fetchChat = async () => {
      if (!threadId) return
      const data = await getChat(threadId)
      setMessages(data.messages)
      setLocalDiagnoses([])
      setLocalSession(data.session)
      setSession(data.session)
    }

    fetchChat()
  }, [threadId, setSession])

  async function handleSend(text: string) {
    if (!threadId) return

    setIsLoading(true)
    setError(null)

    setMessages((prev) => [...prev, { role: "human", content: text }])

    try {
      const response = await sendMessage(threadId, text, i18n.language)
      setMessages(response.messages)
      setLocalSession(response.session)
      setSession(response.session)
    } catch (err) {
      setError(err instanceof Error ? err.message : t("chat.error_unknown"))
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }

  async function handleSendVoice(blob: Blob) {
    if (!threadId) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await sendVoiceMessage(threadId, blob, i18n.language)
      setMessages(response.messages)
      setLocalSession(response.session)
      setSession(response.session)
    } catch (err) {
      setError(err instanceof Error ? err.message : t("chat.error_unknown"))
    } finally {
      setIsLoading(false)
    }
  }

  async function handleGiveUp() {
    if (!threadId) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await giveUp(threadId)
      setMessages(response.messages)
      setLocalSession(response.session)
      setSession(response.session)
      setReportOpen(true)
      refreshUser().catch(() => {})
    } catch (err) {
      setError(err instanceof Error ? err.message : t("chat.error_unknown"))
    } finally {
      setIsLoading(false)
    }
  }

  async function handleDiagnosis(diagnosis: string) {
    if (!threadId) return

    setIsLoading(true)
    setError(null)

    const insertAfterIndex = messages.length - 1
    const diagnosisMsg: Message = {
      role: "human",
      content: diagnosis,
      source: "diagnosis",
    }
    setLocalDiagnoses((prev) => [
      ...prev,
      { msg: diagnosisMsg, insertAfterIndex },
    ])

    try {
      const response = await submitDiagnosis(threadId, diagnosis)
      setMessages(response.messages)
      setLocalDiagnoses([])
      setLocalSession(response.session)
      setSession(response.session)
      if (response.session?.session_summary) {
        setReportOpen(true)
        refreshUser().catch(() => {})
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t("chat.error_unknown"))
      setLocalDiagnoses((prev) => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }

  if (!threadId) return null

  const isSessionEnded =
    localSession?.session_summary != null &&
    localSession.session_summary.length > 0
  const casePresented = messages.some((m) => m.role === "ai")
  const displayMessages = mergeWithDiagnoses(messages, localDiagnoses)

  return (
    <>
      <div className="grid h-full min-h-0 grid-rows-[1fr_auto] grid-cols-1">
        <MessageList
          messages={displayMessages}
          isLoading={isLoading}
          className="overflow-y-auto col-span-1"
        />

        <div className="col-span-1 sm:col-span-2">
          <ErrorBanner error={error} />
          <ModelsStatusBanner />
          <ChatFooter
            isSessionEnded={isSessionEnded}
            hasReport={!!localSession?.final_report}
            onSend={handleSend}
            onSendVoice={handleSendVoice}
            onVoiceError={setError}
            onDiagnosis={handleDiagnosis}
            onGiveUp={handleGiveUp}
            onViewReport={() => setReportOpen(true)}
            diagnosisAttempts={
              localSession
                ? {
                    remaining: localSession.diagnosis_attempts_remaining,
                    total: localSession.diagnosis_attempts_total,
                  }
                : undefined
            }
            disabled={isLoading || modelsStatus === "error"}
            casePresented={casePresented}
          />
        </div>
      </div>

      {localSession?.final_report && (
        <Dialog open={reportOpen} onOpenChange={setReportOpen}>
          <DialogContent className="overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{t("chat.final_report_title")}</DialogTitle>
            </DialogHeader>
            <div className="overflow-y-auto">
              {localSession.module === "radiology" ? (
                <XRayFinalReportPanel
                  report={localSession.final_report as XRayFinalReport}
                />
              ) : (
                <FinalReportPanel
                  report={
                    localSession.final_report as import("@/lib/api").FinalReport
                  }
                />
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}
    </>
  )
}

function ChatFooter({
  isSessionEnded,
  hasReport,
  onSend,
  onSendVoice,
  onVoiceError,
  onDiagnosis,
  onGiveUp,
  onViewReport,
  diagnosisAttempts,
  disabled,
  casePresented,
}: {
  isSessionEnded: boolean
  hasReport: boolean
  onSend: (text: string) => void
  onSendVoice: (blob: Blob) => Promise<void>
  onVoiceError: (message: string) => void
  onDiagnosis: (diagnosis: string) => void
  onGiveUp: () => void
  onViewReport: () => void
  diagnosisAttempts: { remaining: number; total: number } | undefined
  disabled: boolean
  casePresented: boolean
}) {
  const { t } = useTranslation()

  if (isSessionEnded) {
    return (
      <div className="border-t px-4 py-4">
        <div className="max-w-3xl mx-auto rounded-lg bg-muted p-4 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium mb-1">
              {t("chat.session_ended")}
            </p>
          </div>
          {hasReport && (
            <Button
              variant="outline"
              size="sm"
              onClick={onViewReport}
              className="gap-1.5 shrink-0"
            >
              <FileText className="h-4 w-4" />
              {t("chat.view_report")}
            </Button>
          )}
        </div>
      </div>
    )
  }

  return (
    <ChatInput
      onSend={onSend}
      onSendVoice={onSendVoice}
      onVoiceError={onVoiceError}
      onDiagnosis={onDiagnosis}
      onGiveUp={onGiveUp}
      diagnosisAttempts={diagnosisAttempts}
      disabled={disabled}
      casePresented={casePresented}
      onViewReport={hasReport ? onViewReport : undefined}
    />
  )
}

function ErrorBanner({ error }: { error: string | null }) {
  if (!error) return null

  return (
    <div className="px-4 py-2 text-sm text-destructive text-center">
      {error}
    </div>
  )
}
