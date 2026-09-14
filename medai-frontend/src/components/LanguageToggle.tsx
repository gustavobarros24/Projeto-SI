import { useTranslation } from "react-i18next"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { GlobeIcon } from "lucide-react"
import { cn } from "@/lib/utils"

const LANGUAGES = [
  { code: "pt", label: "Português" },
  { code: "en", label: "English" },
]

export function LanguageToggle({ className }: { className?: string }) {
  const { i18n } = useTranslation()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className={cn(
          "inline-flex items-center justify-center rounded-md h-9 w-9 hover:bg-accent hover:text-accent-foreground transition-colors focus-visible:outline-none",
          className,
        )}
      >
        <GlobeIcon className="h-4 w-4" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {LANGUAGES.map(({ code, label }) => (
          <DropdownMenuItem
            key={code}
            onClick={() => i18n.changeLanguage(code)}
            className={i18n.language === code ? "font-semibold" : ""}
          >
            {label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
