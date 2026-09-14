const API_BASE = "http://localhost:8008"

export interface SourceDocument {
  id: string
  title: string
  url: string
}

export interface Message {
  role: "human" | "ai"
  content: string
  source?: "patient" | "tutor" | "presentation" | "responder" | "diagnosis" | null
  source_documents?: SourceDocument[]
  // present on a student turn recorded by voice — id of the stored audio note
  audio_id?: string
}

// TODO: verify types and types attributes, too lazy to see now
export type SessionInfo = AnamnesisSession | XraySession

export interface FinalReport {
  grade: "A" | "B" | "C" | "D" | "F"
  total_points: number
  max_points: number
  strengths: string[]
  improvements: string[]
  overall_feedback: string
  hidden_diagnosis: string
  covered_symptoms_num: number
  all_symptoms_num: number
  all_symptoms: string[]
  covered_symptoms: string[]
  source_documents?: SourceDocument[]
}

export interface XRayFinalReport {
  grade: "A" | "B" | "C" | "D" | "F"
  total_points: number
  max_points: number
  strengths: string[]
  improvements: string[]
  overall_feedback: string
  ground_truth_findings: string[]
  ground_truth_findings_num: number
  correct_impression: string
  correct_findings: string[]
  incorrect_findings: string[]
  source_documents?: SourceDocument[]
}

export interface BaseSession {
  module: "anamnesis" | "radiology"
  turn_count: number
  session_summary: string | null
  diagnosis_attempts_total: number
  diagnosis_attempts_remaining: number
  gave_up: boolean
  final_report?: FinalReport | XRayFinalReport
}

export interface AnamnesisSession extends BaseSession {
  module: "anamnesis"
  covered_symptoms: string[]
  questions_asked: string[]
  consecutive_irrelevant_count: number
}

export interface XraySession extends BaseSession {
  module: "radiology"
  image_url: string | null
  student_findings: string[]
  incorrect_findings: string[]
  consecutive_error_count: number
  ground_truth_findings: string[]
}

export interface ChatResponse {
  messages: Message[]
  session: SessionInfo
}

export interface NewChatResponse extends ChatResponse {
  thread_id: string
}

export async function sendMessage(
  threadId: string,
  message: string,
  language: string = "en",
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ thread_id: threadId, message, language }),
  })

  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

function blobExtension(type: string): string {
  if (type.includes("ogg")) return "ogg"
  if (type.includes("wav")) return "wav"
  if (type.includes("mp4") || type.includes("mpeg")) return "m4a"
  return "webm"
}

// Send a recorded utterance: the backend transcribes it (Gemma 4) and feeds the
// text into the chat graph as the next student turn, returning the updated chat.
export async function sendVoiceMessage(
  threadId: string,
  blob: Blob,
  language: string = "en",
): Promise<ChatResponse> {
  const form = new FormData()
  form.append("file", blob, `recording.${blobExtension(blob.type)}`)
  form.append("thread_id", threadId)
  form.append("language", language)

  const res = await fetch(`${API_BASE}/chat/voice`, {
    method: "POST",
    credentials: "include",
    body: form,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Erro: ${res.status}`)
  }
  return res.json()
}

export function buildAudioUrl(audioId: string): string {
  return `${API_BASE}/voice-notes/${audioId}/file`
}

export async function getChat(threadId: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat/${threadId}`, {
    method: "GET",
    credentials: "include",
  })

  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function createChat(
  message: string,
  language: string = "en",
  anamnesisCaseId?: string,
  radiologyCaseId?: string,
): Promise<NewChatResponse> {
  const body = {
    message,
    anamnesis_case_id: anamnesisCaseId,
    radiology_case_id: radiologyCaseId,
    language,
  }

  const res = await fetch(`${API_BASE}/chats/new`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(body),
  })

  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function getChats(): Promise<
  { thread_id: string; created_at: Date; name: string | null }[]
> {
  const res = await fetch(`${API_BASE}/chats`, {
    method: "GET",
    credentials: "include",
  })

  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function deleteChat(threadId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/chats/${threadId}`, {
    method: "DELETE",
    credentials: "include",
  })

  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
}

export async function giveUp(threadId: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat/${threadId}/give-up`, {
    method: "POST",
    credentials: "include",
  })

  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function submitDiagnosis(
  threadId: string,
  diagnosis: string,
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat/${threadId}/diagnose`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ diagnosis }),
  })

  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function renameChat(
  threadId: string,
  name: string,
): Promise<{ thread_id: string; name: string }> {
  const res = await fetch(`${API_BASE}/chats/${threadId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ name }),
  })

  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export interface ModelsHealth {
  status: "ok" | "error"
  message: string
}

export async function checkModelsHealth(): Promise<ModelsHealth> {
  const res = await fetch(`${API_BASE}/models/health`, {
    method: "GET",
    credentials: "include",
  })

  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export interface DocumentMeta {
  id: string
  filename: string
  mime_type: string
  uploaded_by?: string
  created_at: string
}

export function buildDocumentUrl(documentId: string): string {
  return `${API_BASE}/documents/${documentId}`
}

export async function listDocuments(): Promise<DocumentMeta[]> {
  const res = await fetch(`${API_BASE}/documents`, {
    method: "GET",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function uploadDocument(file: File): Promise<DocumentMeta> {
  const form = new FormData()
  form.append("file", file)
  const res = await fetch(`${API_BASE}/documents`, {
    method: "POST",
    credentials: "include",
    body: form,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Erro: ${res.status}`)
  }
  return res.json()
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: "DELETE",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
}

// ----- Anamnesis cases -----

export type AnamnesisCaseStatus = "draft" | "published"

export interface AnamnesisCaseSummary {
  id: string
  title: string
  description: string
  level: number
}

export interface AnamnesisCaseAdminSummary extends AnamnesisCaseSummary {
  status: AnamnesisCaseStatus
  original_filename: string
  uploaded_by: string
  created_at: string
  updated_at: string
}

export interface AnamnesisCase extends AnamnesisCaseAdminSummary {
  patient_name: string
  patient_age: number
  patient_gender: string
  hidden_diagnosis: string
  symptoms: string[]
  patient_emotional_state: string
  mime_type: string
}

export interface AnamnesisCaseUpdate {
  title?: string
  description?: string
  level?: number
  patient_name?: string
  patient_age?: number
  patient_gender?: string
  hidden_diagnosis?: string
  symptoms?: string[]
  patient_emotional_state?: string
  status?: AnamnesisCaseStatus
}

export interface ExtractedCaseFields {
  patient_name: string
  patient_age: number
  patient_gender: string
  hidden_diagnosis: string
  symptoms: string[]
  patient_emotional_state: string
}

export function buildAnamnesisCaseFileUrl(caseId: string): string {
  return `${API_BASE}/anamnesis-cases/${caseId}/file`
}

export async function listPublishedAnamnesisCases(): Promise<AnamnesisCaseSummary[]> {
  const res = await fetch(`${API_BASE}/anamnesis-cases`, {
    method: "GET",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function listAllAnamnesisCases(): Promise<AnamnesisCaseAdminSummary[]> {
  const res = await fetch(`${API_BASE}/anamnesis-cases/admin`, {
    method: "GET",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function getAnamnesisCase(caseId: string): Promise<AnamnesisCase> {
  const res = await fetch(`${API_BASE}/anamnesis-cases/${caseId}`, {
    method: "GET",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function uploadAnamnesisCase(file: File): Promise<AnamnesisCase> {
  const form = new FormData()
  form.append("file", file)
  const res = await fetch(`${API_BASE}/anamnesis-cases`, {
    method: "POST",
    credentials: "include",
    body: form,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Erro: ${res.status}`)
  }
  return res.json()
}

export async function updateAnamnesisCase(
  caseId: string,
  payload: AnamnesisCaseUpdate,
): Promise<AnamnesisCase> {
  const res = await fetch(`${API_BASE}/anamnesis-cases/${caseId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Erro: ${res.status}`)
  }
  return res.json()
}

export async function reExtractAnamnesisCase(caseId: string): Promise<ExtractedCaseFields> {
  const res = await fetch(`${API_BASE}/anamnesis-cases/${caseId}/re-extract`, {
    method: "POST",
    credentials: "include",
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Erro: ${res.status}`)
  }
  return res.json()
}

export async function deleteAnamnesisCase(caseId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/anamnesis-cases/${caseId}`, {
    method: "DELETE",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
}

// ----- Radiology cases -----

export type RadiologyCaseStatus = "draft" | "published"

export interface RadiologyCaseSummary {
  id: string
  title: string
  level: number
}

export interface RadiologyCaseAdminSummary extends RadiologyCaseSummary {
  status: RadiologyCaseStatus
  original_filename: string
  uploaded_by: string
  created_at: string
  updated_at: string
}

export interface RadiologyCase extends RadiologyCaseAdminSummary {
  ground_findings: string[]
  impression: string
  mime_type: string
}

export interface RadiologyCaseUpdate {
  title?: string
  level?: number
  ground_findings?: string[]
  impression?: string
  status?: RadiologyCaseStatus
}

export interface ExtractedRadiologyFields {
  ground_findings: string[]
  impression: string
}

export function buildRadiologyCaseFileUrl(caseId: string): string {
  return `${API_BASE}/radiology-cases/${caseId}/file`
}

export async function listPublishedRadiologyCases(): Promise<RadiologyCaseSummary[]> {
  const res = await fetch(`${API_BASE}/radiology-cases`, {
    method: "GET",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function listAllRadiologyCases(): Promise<RadiologyCaseAdminSummary[]> {
  const res = await fetch(`${API_BASE}/radiology-cases/admin`, {
    method: "GET",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function getRadiologyCase(caseId: string): Promise<RadiologyCase> {
  const res = await fetch(`${API_BASE}/radiology-cases/${caseId}`, {
    method: "GET",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
  return res.json()
}

export async function uploadRadiologyCase(file: File): Promise<RadiologyCase> {
  const form = new FormData()
  form.append("file", file)
  const res = await fetch(`${API_BASE}/radiology-cases`, {
    method: "POST",
    credentials: "include",
    body: form,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Erro: ${res.status}`)
  }
  return res.json()
}

export async function updateRadiologyCase(
  caseId: string,
  payload: RadiologyCaseUpdate,
): Promise<RadiologyCase> {
  const res = await fetch(`${API_BASE}/radiology-cases/${caseId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Erro: ${res.status}`)
  }
  return res.json()
}

export async function reExtractRadiologyCase(caseId: string): Promise<ExtractedRadiologyFields> {
  const res = await fetch(`${API_BASE}/radiology-cases/${caseId}/re-extract`, {
    method: "POST",
    credentials: "include",
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Erro: ${res.status}`)
  }
  return res.json()
}

export async function deleteRadiologyCase(caseId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/radiology-cases/${caseId}`, {
    method: "DELETE",
    credentials: "include",
  })
  if (!res.ok) throw new Error(`Erro na API: ${res.status}`)
}
