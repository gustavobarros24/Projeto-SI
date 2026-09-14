import { CheckCircle, TrendingUp, MessageSquare, Stethoscope, Award, CircleDot } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { FinalReport } from "@/lib/api"
import { cn } from "@/lib/utils"
import { useTranslation } from "react-i18next"
import { SourceDocumentButtons } from "@/components/SourceDocumentButtons"

const GRADE_STYLE: Record<FinalReport["grade"], { color: string; stroke: string; bg: string }> = {
  A: { color: "text-emerald-600 dark:text-emerald-400", stroke: "stroke-emerald-500", bg: "bg-emerald-50 dark:bg-emerald-950 border-emerald-200 dark:border-emerald-800" },
  B: { color: "text-blue-600 dark:text-blue-400", stroke: "stroke-blue-500", bg: "bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800" },
  C: { color: "text-yellow-600 dark:text-yellow-400", stroke: "stroke-yellow-500", bg: "bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800" },
  D: { color: "text-orange-600 dark:text-orange-400", stroke: "stroke-orange-500", bg: "bg-orange-50 dark:bg-orange-950 border-orange-200 dark:border-orange-800" },
  F: { color: "text-red-600 dark:text-red-400", stroke: "stroke-red-500", bg: "bg-red-50 dark:bg-red-950 border-red-200 dark:border-red-800" },
}

function CircularProgress({ pct, stroke, children }: { pct: number; stroke: string; children: React.ReactNode }) {
  const r = 36
  const circumference = 2 * Math.PI * r
  const offset = circumference * (1 - pct / 100)
  return (
    <div className="relative flex items-center justify-center w-24 h-24">
      <svg className="-rotate-90 absolute inset-0 w-full h-full">
        <circle cx="48" cy="48" r={r} fill="none" strokeWidth="6" className="stroke-muted" />
        <circle
          cx="48" cy="48" r={r} fill="none" strokeWidth="6"
          className={cn("transition-all duration-500", stroke)}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <div className="relative flex flex-col items-center justify-center">
        {children}
      </div>
    </div>
  )
}

export function FinalReportPanel({ report }: { report: FinalReport }) {
  const { t } = useTranslation()
  const style = GRADE_STYLE[report.grade] ?? GRADE_STYLE["F"]
  const gradeLabel = t(`report.grades.${report.grade}`)
  const symptomPct = (report.all_symptoms_num ?? 0) > 0
    ? Math.round(((report.covered_symptoms_num ?? 0) / report.all_symptoms_num) * 100)
    : 0
  const pointsPct = (report.max_points ?? 0) > 0
    ? Math.round(((report.total_points ?? 0) / report.max_points) * 100)
    : 0

  return (
    <div className="space-y-3 max-w-2xl mx-auto py-4 px-4">

      {/* topo: esquerda (grade+pontos+diagnóstico) | direita (sintomas) */}
      <div className="grid grid-cols-2 gap-3 items-stretch">

        {/* coluna esquerda */}
        <div className="flex flex-col gap-3">
          {/* grade + pontos lado a lado */}
          <div className="grid grid-cols-2 gap-3">
            <Card className={cn("border relative flex flex-col", style.bg)}>
              <Award className={cn("absolute top-2 left-2 h-5 w-5", style.color)} />
              <div className="flex-1 flex items-center justify-center pt-4">
                <span className={cn("text-4xl font-bold", style.color)}>{report.grade}</span>
              </div>
              <div className="pb-3 flex justify-center">
                <span className="text-xs text-muted-foreground">{gradeLabel}</span>
              </div>
            </Card>

            <Card>
              <CardContent className="flex flex-col items-center justify-center py-3">
                <CircularProgress pct={pointsPct} stroke={style.stroke}>
                  <span className="text-2xl font-bold leading-none">{report.total_points}</span>
                  <span className="text-[10px] text-muted-foreground">/ {report.max_points}</span>
                </CircularProgress>
                <span className="text-xs text-muted-foreground mt-1">{t("report.points")}</span>
              </CardContent>
            </Card>
          </div>

          {/* diagnóstico correto */}
          <Card>
            <CardHeader className="pb-1">
              <CardTitle className="flex items-center gap-1.5 text-sm">
                <Stethoscope className="h-4 w-4 text-muted-foreground" />
                {t("report.correct_diagnosis")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <span className="block w-full rounded-md bg-muted px-3 py-1.5 text-sm font-semibold">
                {report.hidden_diagnosis}
              </span>
            </CardContent>
          </Card>
        </div>

        {/* coluna direita — sintomas */}
        <Card className="flex flex-col">
          <CardHeader className="pb-2 shrink-0">
            <CardTitle className="text-sm">
              {t("report.symptoms")} — {report.covered_symptoms_num}/{report.all_symptoms_num}
            </CardTitle>
            <div className="w-full bg-muted rounded-full h-1.5 mt-1">
              <div
                className="h-1.5 rounded-full bg-primary transition-all"
                style={{ width: `${symptomPct}%` }}
              />
            </div>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto">
            <ul className="space-y-2">
              {(report.all_symptoms ?? []).map((symptom) => {
                const covered = report.covered_symptoms.some(
                  (s) => s.toLowerCase() === symptom.toLowerCase()
                )
                return (
                  <li key={symptom} className="flex items-center gap-2 text-sm">
                    {covered
                      ? <CheckCircle className="h-4 w-4 text-emerald-500 shrink-0" />
                      : <CircleDot className="h-4 w-4 text-muted-foreground/40 shrink-0" />
                    }
                    <span className={covered ? "" : "text-muted-foreground"}>{symptom}</span>
                  </li>
                )
              })}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* pontos fortes + a melhorar */}
      <div className="grid grid-cols-2 gap-3">
        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-1.5 text-sm text-emerald-600 dark:text-emerald-400">
              <CheckCircle className="h-4 w-4" />
              {t("report.strengths")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              {(report.strengths ?? []).map((s, i) => (
                <li key={i} className="text-xs text-muted-foreground flex gap-1.5">
                  <span className="text-emerald-500 shrink-0">+</span>
                  {s}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-1">
            <CardTitle className="flex items-center gap-1.5 text-sm text-orange-600 dark:text-orange-400">
              <TrendingUp className="h-4 w-4" />
              {t("report.improvements")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              {(report.improvements ?? []).map((s, i) => (
                <li key={i} className="text-xs text-muted-foreground flex gap-1.5">
                  <span className="text-orange-500 shrink-0">↑</span>
                  {s}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* feedback geral */}
      <Card>
        <CardHeader className="pb-1">
          <CardTitle className="flex items-center gap-1.5 text-sm">
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
            {t("report.tutor_feedback")}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground italic leading-relaxed">
            "{report.overall_feedback}"
          </p>
          <SourceDocumentButtons sources={report.source_documents} />
        </CardContent>
      </Card>
    </div>
  )
}
