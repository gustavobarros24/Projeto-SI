import { createContext, useContext, useState } from "react"
import type { SessionInfo } from "@/lib/api"

interface SessionContextProps {
  session: SessionInfo | null
  setSession: (session: SessionInfo | null) => void
}

const SessionContext = createContext<SessionContextProps | null>(null)

export function useSession() {
  const context = useContext(SessionContext)
  if (!context) {
    throw new Error("useSession must be used within a SessionProvider.")
  }

  return context
}

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<SessionInfo | null>(null)

  return (
    <SessionContext.Provider value={{ session, setSession }}>
      {children}
    </SessionContext.Provider>
  )
}
