import { useTranslation } from "react-i18next"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

import { AnamnesisCasesTab } from "./teacher-documents/AnamnesisCasesTab"
import { RadiologyCasesTab } from "./teacher-documents/RadiologyCasesTab"
import { RagDocumentsTab } from "./teacher-documents/RagDocumentsTab"

export default function TeacherDocumentsPage() {
  const { t } = useTranslation()

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-4">
      <h1 className="text-2xl font-semibold">
        {t("teacher.documents.title")}
      </h1>
      <p className="text-sm text-muted-foreground">
        {t("teacher.documents.description")}
      </p>

      <Tabs defaultValue="rag">
        <TabsList>
          <TabsTrigger value="rag">{t("teacher.tabs.rag")}</TabsTrigger>
          <TabsTrigger value="cases">{t("teacher.tabs.cases")}</TabsTrigger>
          <TabsTrigger value="radiology">{t("teacher.tabs.radiology_cases")}</TabsTrigger>
        </TabsList>
        <TabsContent value="rag">
          <RagDocumentsTab />
        </TabsContent>
        <TabsContent value="cases">
          <AnamnesisCasesTab />
        </TabsContent>
        <TabsContent value="radiology">
          <RadiologyCasesTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
