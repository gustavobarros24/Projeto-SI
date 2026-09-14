import { Navigate } from "react-router"
import { useAuth } from "@/contexts/AuthContext"
import { useTranslation } from "react-i18next"
import type { ReactNode } from "react"

interface Props {
  children: ReactNode
  requireTeacher?: boolean
}

export function ProtectedRoute({ children, requireTeacher = false }: Props) {
  const { user, isLoading } = useAuth()
  const { t } = useTranslation()

  if (isLoading) {
    return (
      <div className="flex h-dvh items-center justify-center">
        <p className="text-muted-foreground">{t("common.loading")}</p>
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />
  if (requireTeacher && user.role !== "teacher") return <Navigate to="/chat" replace />

  return children
}
