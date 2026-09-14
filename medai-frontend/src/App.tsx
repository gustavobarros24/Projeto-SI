import { Routes, Route, Navigate, useLocation } from "react-router"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { AuthProvider } from "@/contexts/AuthContext"
import { ProtectedRoute } from "@/components/ProtectedRoute"
import { LanguageToggle } from "@/components/LanguageToggle"
import LoginPage from "@/pages/LoginPage"
import SignupPage from "@/pages/SignupPage"
import TeacherDocumentsPage from "@/pages/TeacherDocumentsPage"
import { ChatPage } from "@/features/chat/pages/ChatPage"
import { NewChatPage } from "./features/chat/pages/NewChatPage"

const queryClient = new QueryClient()

function AuthLanguageToggle() {
  const { pathname } = useLocation()
  if (pathname.startsWith("/chat")) return null
  return <LanguageToggle className="fixed top-4 right-4 z-50" />
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AuthLanguageToggle />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="/chat/:threadId"
            element={
              <ProtectedRoute>
                <ChatPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <NewChatPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/teacher/documents"
            element={
              <ProtectedRoute requireTeacher>
                <TeacherDocumentsPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Routes>
      </AuthProvider>
    </QueryClientProvider>
  )
}
