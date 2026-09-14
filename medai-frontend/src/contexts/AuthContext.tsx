import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { getMe, login as apiLogin, signup as apiSignup, logout as apiLogout, type User } from "@/lib/auth"

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setIsLoading(false))
  }, [])

  async function login(email: string, password: string) {
    const u = await apiLogin(email, password)
    setUser(u)
  }

  async function signup(name: string, email: string, password: string) {
    const u = await apiSignup(name, email, password)
    setUser(u)
  }

  async function logout() {
    await apiLogout()
    setUser(null)
  }

  async function refreshUser() {
    const u = await getMe()
    setUser(u)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, signup, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
