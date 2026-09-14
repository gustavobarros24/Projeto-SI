import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import { Progress } from "@/components/ui/progress"
import { ChevronDownIcon, ChevronUpIcon } from "lucide-react"
import { useState } from "react"
import { useTranslation } from "react-i18next"

interface StatCardProps {
  icon: React.ReactNode
  label: string
  value: string
  progress?: number
  list?: string[]
}

export function StatCard({
  icon,
  label,
  value,
  progress,
  list,
}: StatCardProps) {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(true)

  return (
    <Card>
      <CardContent>
        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <div className="flex items-center gap-3">
            <div className="text-muted-foreground">{icon}</div>

            <div className="flex-1 min-w-0">
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-sm font-semibold">{value}</p>
            </div>

            {list && (
              <CollapsibleTrigger>
                <Button variant="ghost" size="icon" className="size-8">
                  {isOpen ? <ChevronUpIcon /> : <ChevronDownIcon />}
                  <span className="sr-only">{t("stat_card.toggle_details")}</span>
                </Button>
              </CollapsibleTrigger>
            )}
          </div>

          <CollapsibleContent className="flex flex-col gap-2 divide-y">
            {list?.map((item) => (
              <p key={item} className="py-1.5 text-muted-foreground">
                {item}
              </p>
            ))}
          </CollapsibleContent>
        </Collapsible>
      </CardContent>

      {progress !== undefined && (
        <CardFooter>
          <Progress value={progress} className="w-full" />
        </CardFooter>
      )}
    </Card>
  )
}
