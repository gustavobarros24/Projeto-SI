import { useEffect, useRef, useState } from "react"
import { Button } from "@/components/ui/button"
import { Mic, Square, Loader2 } from "lucide-react"
import { useTranslation } from "react-i18next"
import { blobToWav16kMono } from "@/lib/audio"

// Stay safely under Gemma 4's 30s-per-clip transcription limit.
const MAX_RECORDING_MS = 28_000

type RecState = "idle" | "recording" | "processing"

interface MicButtonProps {
  onRecorded?: (blob: Blob) => Promise<void>
  onError?: (message: string) => void
  disabled?: boolean
}

export function MicButton({ onRecorded, onError, disabled }: MicButtonProps) {
  const { t } = useTranslation()
  const [state, setState] = useState<RecState>("idle")
  const [elapsed, setElapsed] = useState(0)

  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const streamRef = useRef<MediaStream | null>(null)
  const timerRef = useRef<number | null>(null)
  const autoStopRef = useRef<number | null>(null)

  useEffect(() => {
    return () => {
      stopTracks()
      clearTimers()
    }
  }, [])

  function stopTracks() {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null
  }

  function clearTimers() {
    if (timerRef.current) {
      window.clearInterval(timerRef.current)
      timerRef.current = null
    }
    if (autoStopRef.current) {
      window.clearTimeout(autoStopRef.current)
      autoStopRef.current = null
    }
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      chunksRef.current = []

      const recorder = new MediaRecorder(stream)
      recorderRef.current = recorder
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }
      recorder.onstop = handleStop
      recorder.start()

      setState("recording")
      setElapsed(0)
      timerRef.current = window.setInterval(() => setElapsed((s) => s + 1), 1000)
      autoStopRef.current = window.setTimeout(stopRecording, MAX_RECORDING_MS)
    } catch {
      onError?.(t("chat.input.mic_permission_denied"))
    }
  }

  function stopRecording() {
    clearTimers()
    const recorder = recorderRef.current
    if (recorder && recorder.state !== "inactive") {
      recorder.stop()
    }
  }

  async function handleStop() {
    const recorder = recorderRef.current
    stopTracks()
    const blob = new Blob(chunksRef.current, {
      type: recorder?.mimeType || "audio/webm",
    })
    chunksRef.current = []

    if (blob.size === 0) {
      setState("idle")
      onError?.(t("chat.input.mic_error"))
      return
    }

    setState("processing")
    try {
      const wav = await blobToWav16kMono(blob)
      await onRecorded?.(wav)
    } catch {
      onError?.(t("chat.input.mic_error"))
    } finally {
      setState("idle")
      setElapsed(0)
    }
  }

  function handleClick() {
    if (state === "recording") {
      stopRecording()
    } else if (state === "idle") {
      startRecording()
    }
  }

  if (!onRecorded) return null

  return (
    <div className="flex items-center gap-1 shrink-0">
      <Button
        type="button"
        variant={state === "recording" ? "destructive" : "ghost"}
        size="icon"
        onClick={handleClick}
        disabled={disabled || state === "processing"}
        title={micTitle(t, state)}
      >
        <MicIcon state={state} />
      </Button>
      <RecordingTimer state={state} elapsed={elapsed} />
    </div>
  )
}

function micTitle(t: (k: string) => string, state: RecState): string {
  switch (state) {
    case "recording":
      return t("chat.input.recording")
    case "processing":
      return t("chat.input.transcribing")
    default:
      return t("chat.input.record")
  }
}

function MicIcon({ state }: { state: RecState }) {
  if (state === "processing") return <Loader2 className="h-4 w-4 animate-spin" />
  if (state === "recording") return <Square className="h-4 w-4" />
  return <Mic className="h-4 w-4" />
}

function RecordingTimer({ state, elapsed }: { state: RecState; elapsed: number }) {
  if (state !== "recording") return null
  const ss = String(elapsed % 60).padStart(2, "0")
  return (
    <span className="text-xs tabular-nums text-destructive">
      {Math.floor(elapsed / 60)}:{ss}
    </span>
  )
}
