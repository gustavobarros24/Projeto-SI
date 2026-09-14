const API_BASE = "http://localhost:8008"

export interface User {
  id: string
  name: string
  email: string
  role: "student" | "teacher"
  anamnesis_level: number
  anamnesis_xp: number
  radiology_level: number
  radiology_xp: number
}

async function authFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    ...options,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Erro: ${res.status}`)
  }

  return res.json()
}

export function signup(name: string, email: string, password: string) {
  return authFetch<User>("/auth/signup", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  })
}

export function login(email: string, password: string) {
  return authFetch<User>("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  })
}

export async function logout() {
  await authFetch<{ detail: string }>("/auth/logout", { method: "POST" })
}

export function getMe() {
  return authFetch<User>("/auth/me")
}
