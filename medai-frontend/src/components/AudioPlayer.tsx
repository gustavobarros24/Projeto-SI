import { buildAudioUrl } from "@/lib/api"

// Renders a playable mini-player for a student's recorded voice turn.
// Early-returns null for typed messages (no audio_id), mirroring SourceDocumentButtons.
export function AudioPlayer({ audioId }: { audioId?: string }) {
  if (!audioId) return null

  return (
    <audio
      controls
      preload="none"
      src={buildAudioUrl(audioId)}
      className="mt-2 h-9 w-full max-w-[260px]"
    />
  )
}
