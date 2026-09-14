import { useEffect, useRef } from "react"
import type { Message } from "@/lib/api"
import { ScrollArea } from "@/components/ui/scroll-area"
import { MessageBubble } from "@/components/MessageBubble"

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
  className?: string
}

export function MessageList({ messages, isLoading, className }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  return (
    <ScrollArea className={`flex-1 px-4 ${className ?? ""}`}>
      <div className="max-w-3xl mx-auto py-4">
        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            role={msg.role}
            content={msg.content}
            source={msg.source}
            source_documents={msg.source_documents}
            audio_id={msg.audio_id}
          />
        ))}
        {isLoading && (
          <div className="flex items-end gap-2 mb-4">
            <div className="bg-muted rounded-lg px-4 py-2">
              <span className="flex gap-1">
                <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:0ms]" />
                <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:150ms]" />
                <span className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce [animation-delay:300ms]" />
              </span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  )
}
