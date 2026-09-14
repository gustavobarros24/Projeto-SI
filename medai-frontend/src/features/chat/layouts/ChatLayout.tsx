import { useEffect, useState } from "react"
import { useParams } from "react-router"
import { AppSidebar } from "@/components/AppSidebar"
import { SidebarProvider } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { PanelLeftIcon, PanelRightIcon } from "lucide-react"
import { RightSidebar } from "@/features/chat/components/RightSidebar"
import { SessionProvider } from "@/contexts/SessionContext"
import { ModelsStatusPill } from "@/components/ModelsStatusPill"
import { LanguageToggle } from "@/components/LanguageToggle"
import { useTranslation } from "react-i18next"

interface ChatLayoutProps {
  children: React.ReactNode
}

export function ChatLayout({ children }: ChatLayoutProps) {
  return (
    <SessionProvider>
      <ChatLayoutContent>{children}</ChatLayoutContent>
    </SessionProvider>
  )
}

function ChatLayoutContent({ children }: ChatLayoutProps) {
  const { t } = useTranslation()
  const { threadId } = useParams<{ threadId: string }>()
  const [leftOpen, setLeftOpen] = useState(true)
  const [rightOpen, setRightOpen] = useState(false)

  // Only show right sidebar if there's a thread, otherwise it just takes up space for no reason
  const hasThread = Boolean(threadId)
  useEffect(() => {
    setRightOpen(hasThread)
  }, [hasThread])

  return (
    <div className="flex h-svh w-full bg-sidebar">
      <SidebarProvider
        open={leftOpen}
        onOpenChange={setLeftOpen}
        className="w-auto min-h-0 flex-none"
      >
        <AppSidebar />
      </SidebarProvider>

      <div className="relative flex min-w-0 flex-1 flex-col bg-background md:m-2 md:ml-0 md:rounded-xl md:shadow-sm overflow-hidden">
        <header className="flex items-center gap-2 px-4 py-3 border-b shrink-0">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setLeftOpen((v) => !v)}
          >
            <PanelLeftIcon />
          </Button>

          <h1 className="text-lg font-semibold flex-1">
            {t("common.app_name")}
          </h1>

          <div className="flex items-center gap-2">
            <div className="-translate-y-px">
              <ModelsStatusPill />
            </div>
            <LanguageToggle />
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setRightOpen((v) => !v)}
          >
            <PanelRightIcon />
          </Button>
        </header>

        <main className="flex-1 overflow-hidden">{children}</main>
      </div>

      <SidebarProvider
        open={rightOpen}
        onOpenChange={setRightOpen}
        className="w-auto min-h-0 flex-none"
        style={
          {
            "--sidebar-width": "28rem",
            "--sidebar-width-mobile": "20rem",
          } as React.CSSProperties
        }
      >
        <RightSidebar />
      </SidebarProvider>
    </div>
  )
}
