// The STT model (Gemma 4 via llama.cpp) only accepts `wav` or `mp3`, while
// MediaRecorder produces webm/opus. We convert in the browser using the native
// Web Audio API — no extra dependency — to a 16 kHz mono WAV (the format the
// model expects), so the backend can forward it untouched.

const TARGET_SAMPLE_RATE = 16000

export async function blobToWav16kMono(blob: Blob): Promise<Blob> {
  const arrayBuffer = await blob.arrayBuffer()

  // Decode the compressed recording to PCM via the browser's native decoder.
  const decodeCtx = new AudioContext()
  let decoded: AudioBuffer
  try {
    decoded = await decodeCtx.decodeAudioData(arrayBuffer)
  } finally {
    decodeCtx.close()
  }

  // Resample to 16 kHz mono.
  const frameCount = Math.max(1, Math.ceil(decoded.duration * TARGET_SAMPLE_RATE))
  const offline = new OfflineAudioContext(1, frameCount, TARGET_SAMPLE_RATE)
  const source = offline.createBufferSource()
  source.buffer = decoded
  source.connect(offline.destination)
  source.start()
  const rendered = await offline.startRendering()

  return encodeWav(rendered.getChannelData(0), TARGET_SAMPLE_RATE)
}

function encodeWav(samples: Float32Array, sampleRate: number): Blob {
  const dataSize = samples.length * 2 // 16-bit mono
  const view = new DataView(new ArrayBuffer(44 + dataSize))

  const writeString = (offset: number, str: string) => {
    for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i))
  }

  writeString(0, "RIFF")
  view.setUint32(4, 36 + dataSize, true)
  writeString(8, "WAVE")
  writeString(12, "fmt ")
  view.setUint32(16, 16, true) // fmt chunk size
  view.setUint16(20, 1, true) // PCM
  view.setUint16(22, 1, true) // mono
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * 2, true) // byte rate (sampleRate * blockAlign)
  view.setUint16(32, 2, true) // block align (channels * bytesPerSample)
  view.setUint16(34, 16, true) // bits per sample
  writeString(36, "data")
  view.setUint32(40, dataSize, true)

  let offset = 44
  for (let i = 0; i < samples.length; i++) {
    const s = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true)
    offset += 2
  }

  return new Blob([view], { type: "audio/wav" })
}
