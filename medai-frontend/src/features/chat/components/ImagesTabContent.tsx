import type { SessionInfo } from "@/lib/api"
import { ImageIcon, MaximizeIcon, XIcon } from "lucide-react"
import { useState } from "react"
import { useTranslation } from "react-i18next"

interface ImagesTabContentProps {
  session: SessionInfo | null
}

export function ImagesTabContent({ session }: ImagesTabContentProps) {
  const { t } = useTranslation()
  const [fullscreen, setFullscreen] = useState(false)

  if (!session || session.module !== "radiology" || !session.image_url) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <ImageIcon className="size-10 mb-2 opacity-50" />
        <p className="text-sm">{t("images.no_image")}</p>
      </div>
    )
  }

  return (
    <>
      <button
        type="button"
        className="group relative cursor-pointer rounded-lg overflow-hidden"
        onClick={() => setFullscreen(true)}
      >
        <img
          src={session.image_url}
          alt={t("images.xray_alt")}
          className="max-w-full object-contain rounded-lg"
        />
        <div className="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/40 transition-colors">
          <MaximizeIcon className="size-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </button>

      <ImageFullscreen
        imageUrl={session.image_url}
        open={fullscreen}
        onClose={() => setFullscreen(false)}
      />
    </>
  )
}

interface ImageFullscreenProps {
  imageUrl: string
  open: boolean
  onClose: () => void
}

function ImageFullscreen({ imageUrl, open, onClose }: ImageFullscreenProps) {
  const { t } = useTranslation()

  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 animate-in fade-in duration-200"
      onClick={onClose}
    >
      <button
        type="button"
        className="absolute top-4 right-4 text-white/70 hover:text-white transition-colors cursor-pointer"
        onClick={onClose}
      >
        <XIcon className="size-8" />
      </button>

      <img
        src={imageUrl}
        alt={t("images.xray_alt")}
        className="max-h-[90vh] max-w-[90vw] object-contain"
        onClick={(e) => e.stopPropagation()}
      />
    </div>
  )
}
