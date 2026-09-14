import { useState } from "react"
import { useNavigate } from "react-router"
import { createChat, type Message } from "@/lib/api"
import { useModelsHealth } from "@/hooks/use-models-health"
import { MessageList } from "@/components/MessageList"
import { ChatInput } from "@/components/ChatInput"
import { ModelsStatusBanner } from "@/components/ModelsStatusBanner"
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { AnamnesisModal } from "./AnamnesisModal"
import { RadiologyModal } from "./RadiologyModal"
import { useTranslation } from "react-i18next"

export function NewChat() {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const { status: modelsStatus } = useModelsHealth()
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [radiologyModalOpen, setRadiologyModalOpen] = useState(false)
  const [anamnesisModalOpen, setAnamnesisModalOpen] = useState(false)
  const modelsDown = modelsStatus === "error"

  async function handleSend(
    text: string,
    anamnesisCaseId?: string,
    radiologyCaseId?: string,
  ) {
    setIsLoading(true)
    setError(null)

    setMessages([{ role: "human", content: text }])

    try {
      const response = await createChat(
        text,
        i18n.language,
        anamnesisCaseId,
        radiologyCaseId,
      )
      navigate(`/chat/${response.thread_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : t("chat.error_unknown"))
      setMessages([])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="grid h-full min-h-0 grid-rows-[1fr_auto] grid-cols-1">
      <ChatArea
        messages={messages}
        isLoading={isLoading}
        modelsDown={modelsDown}
        onSelectAnamnesis={() => setAnamnesisModalOpen(true)}
        onSelectRadiology={() => setRadiologyModalOpen(true)}
      />
      <AnamnesisModal
        open={anamnesisModalOpen}
        onOpenChange={setAnamnesisModalOpen}
        onSelect={(caseId) => {
          setAnamnesisModalOpen(false)
          handleSend(t("new_chat.anamnesis.start_message"), caseId)
        }}
      />
      <RadiologyModal
        open={radiologyModalOpen}
        onOpenChange={setRadiologyModalOpen}
        onSelect={(caseId) => {
          setRadiologyModalOpen(false)
          handleSend(t("new_chat.radiology.start_message"), undefined, caseId)
        }}
      />

      <div className="col-span-1">
        <ErrorBanner error={error} />
        <ModelsStatusBanner />
        <ChatInput onSend={handleSend} disabled={isLoading || modelsDown} casePresented={false} />
      </div>
    </div>
  )
}

interface ChatAreaProps {
  messages: Message[]
  isLoading: boolean
  modelsDown: boolean
  onSelectAnamnesis: () => void
  onSelectRadiology: () => void
}

function ChatArea({ messages, isLoading, modelsDown, onSelectAnamnesis, onSelectRadiology }: ChatAreaProps) {
  const { t } = useTranslation()

  if (messages.length > 0) {
    return (
      <MessageList
        messages={messages}
        isLoading={isLoading}
        className="overflow-y-auto col-span-1"
      />
    )
  }

  return (
    <div className="flex flex-col items-center justify-center overflow-y-auto col-span-1">
      <h2 className="font-semibold mb-8 text-4xl">
        {t("new_chat.choose_module")}
      </h2>

      <div className="flex w-full px-10 gap-12 max-w-7xl justify-center">
        <Card className="w-full flex flex-col max-w-md">
          <CardHeader>
            <CardTitle>{t("new_chat.anamnesis.title")}</CardTitle>
            <CardDescription>
              {t("new_chat.anamnesis.description")}
            </CardDescription>
          </CardHeader>
          <CardFooter className="mt-auto">
            <Button className="w-full" onClick={onSelectAnamnesis} disabled={modelsDown}>
              {t("new_chat.anamnesis.select")}
            </Button>
          </CardFooter>
        </Card>

        <Card className="w-full flex flex-col max-w-md">
          <CardHeader>
            <CardTitle>{t("new_chat.radiology.title")}</CardTitle>
            <CardDescription>
              {t("new_chat.radiology.description")}
            </CardDescription>
          </CardHeader>
          <CardFooter className="mt-auto">
            <Button className="w-full" onClick={onSelectRadiology} disabled={modelsDown}>
              {t("new_chat.radiology.select")}
            </Button>
          </CardFooter>
        </Card>
      </div>
    </div>
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
