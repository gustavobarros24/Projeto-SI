import { useSession } from "@/contexts/SessionContext"
import type { SessionInfo } from "@/lib/api"
import { Sidebar, SidebarContent, SidebarHeader } from "@/components/ui/sidebar"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ProgressTabContent } from "./ProgressTabContent"
import { ImagesTabContent } from "./ImagesTabContent"
import { useTranslation } from "react-i18next"

export function RightSidebar() {
  const { session } = useSession()
  const { t } = useTranslation()

  return (
    <Sidebar side="right" variant="inset" collapsible="offcanvas">
      <Tabs defaultValue="progress" className="flex min-h-0 flex-1 flex-col">
        <SidebarHeader className="p-3">
          <TabsList className="w-full">
            <ImagesTabTrigger session={session} />
            <TabsTrigger value="progress" className="flex-1">
              {t("progress.title")}
            </TabsTrigger>
          </TabsList>
        </SidebarHeader>

        <SidebarContent className="p-3">
          <ImagesTabPanel session={session} />
          <TabsContent value="progress" className="mt-0">
            <ProgressTabContent session={session} />
          </TabsContent>
        </SidebarContent>
      </Tabs>
    </Sidebar>
  )
}

function ImagesTabTrigger({ session }: { session: SessionInfo | null }) {
  const { t } = useTranslation()

  // the Images tab only applies to radiology sessions (anamnesis has no image).
  if (session?.module !== "radiology") return null

  return (
    <TabsTrigger value="images" className="flex-1">
      {t("images.tab")}
    </TabsTrigger>
  )
}

function ImagesTabPanel({ session }: { session: SessionInfo | null }) {
  if (session?.module !== "radiology") return null

  return (
    <TabsContent value="images" className="mt-0">
      <ImagesTabContent session={session} />
    </TabsContent>
  )
}
