import {
  ChevronsUpDownIcon,
  EllipsisVertical,
  EyeIcon,
  FileTextIcon,
  LogOutIcon,
  PencilIcon,
  SquarePenIcon,
  Trash2Icon,
  UserIcon,
} from "lucide-react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import * as z from "zod"
import { Avatar, AvatarFallback } from "./ui/avatar"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
} from "./ui/sidebar"
import { useAuth } from "@/contexts/AuthContext"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog"
import { Button } from "./ui/button"
import { Progress } from "./ui/progress"
import { Field, FieldError, FieldGroup, FieldLabel } from "./ui/field"
import { Input } from "./ui/input"
import { progressForXp, type LevelProgress } from "@/lib/progression"
import { useIsMobile } from "@/hooks/use-mobile"
import { logout } from "@/lib/auth"
import { Link, useNavigate, useParams } from "react-router"
import { useEffect, useMemo, useState } from "react"
import { deleteChat, getChats, renameChat } from "@/lib/api"
import { useTranslation } from "react-i18next"

type Session = {
  thread_id: string
  created_at: Date
  name: string | null
}

export function AppSidebar() {
  const { user } = useAuth()
  const { t } = useTranslation()
  const isMobile = useIsMobile()
  const navigate = useNavigate()

  if (!user) return null

  async function handleLogout() {
    await logout()
    navigate("/login", { replace: true })
  }

  function handleNewChat() {
    navigate("/chat")
  }

  return (
    <Sidebar variant="inset" collapsible="icon">
      <SidebarHeader />

      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton
                className="text-sidebar-foreground/70"
                tooltip={t("sidebar.new_session")}
                onClick={handleNewChat}
              >
                <SquarePenIcon className="text-sidebar-foreground/70" />
                <span>{t("sidebar.new_session")}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <TeacherDocumentsLink />
          </SidebarMenu>
        </SidebarGroup>

        <SidebarGroup className="group-data-[collapsible=icon]:hidden">
          <SidebarGroupLabel>{t("sidebar.sessions")}</SidebarGroupLabel>
          <SidebarMenu>
            <SessionsList />
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <StudentLevelProgress />
        <DropdownMenu>
          <DropdownMenuTrigger>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            >
              <Avatar className="size-8 rounded-lg">
                <AvatarFallback className="rounded-lg">
                  <UserIcon className="size-4" />
                </AvatarFallback>
              </Avatar>

              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium">{user.name}</span>
                <span className="truncate text-xs">{user.email}</span>
              </div>

              <ChevronsUpDownIcon className="ml-auto size-4" />
            </SidebarMenuButton>
          </DropdownMenuTrigger>

          <DropdownMenuContent
            className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
            side={isMobile ? "bottom" : "right"}
            align="end"
            sideOffset={4}
          >
            <DropdownMenuItem onClick={handleLogout}>
              <LogOutIcon />
              {t("sidebar.logout")}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </SidebarFooter>
    </Sidebar>
  )
}

function TeacherDocumentsLink() {
  const { user } = useAuth()
  const { t } = useTranslation()
  const navigate = useNavigate()
  if (!user || user.role !== "teacher") return null
  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        className="text-sidebar-foreground/70"
        tooltip={t("sidebar.documents")}
        onClick={() => navigate("/teacher/documents")}
      >
        <FileTextIcon className="text-sidebar-foreground/70" />
        <span>{t("sidebar.documents")}</span>
      </SidebarMenuButton>
    </SidebarMenuItem>
  )
}

function StudentLevelProgress() {
  const { user } = useAuth()
  const { t } = useTranslation()
  if (!user || user.role !== "student") return null
  const anamnesisProgress = progressForXp(user.anamnesis_xp)
  const radiologyProgress = progressForXp(user.radiology_xp)
  return (
    <div className="flex flex-col gap-3 px-2 py-2 group-data-[collapsible=icon]:hidden">
      <LevelProgressBar
        label={t("sidebar.anamnesis_level", { level: anamnesisProgress.level })}
        progress={anamnesisProgress}
      />
      <LevelProgressBar
        label={t("sidebar.radiology_level", { level: radiologyProgress.level })}
        progress={radiologyProgress}
      />
    </div>
  )
}

function LevelProgressBar({ label, progress }: { label: string; progress: LevelProgress }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-sidebar-foreground/70">{label}</span>
        <LevelXpLabel progress={progress} />
      </div>
      <Progress value={progress.percent} className="gap-0" />
    </div>
  )
}

function LevelXpLabel({ progress }: { progress: LevelProgress }) {
  const { t } = useTranslation()
  if (progress.isMax) {
    return (
      <span className="text-xs text-sidebar-foreground/50">
        {t("sidebar.max_level")}
      </span>
    )
  }
  return (
    <span className="text-xs text-sidebar-foreground/50 tabular-nums">
      {t("sidebar.xp_to_next", { xp: progress.xpIntoLevel, next: progress.xpForLevel })}
    </span>
  )
}

function SessionsList() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [renameTarget, setRenameTarget] = useState<Session | null>(null)

  useEffect(() => {
    const fetchChats = async () => {
      const data = await getChats()
      setSessions(data)
    }

    fetchChats()
  }, [])

  function handleDelete(threadId: string) {
    setSessions((prev) => prev.filter((s) => s.thread_id !== threadId))
  }

  function handleRenamed(threadId: string, name: string) {
    setSessions((prev) =>
      prev.map((s) => (s.thread_id === threadId ? { ...s, name } : s)),
    )
  }

  return (
    <>
      <SessionsRows
        sessions={sessions}
        onDelete={handleDelete}
        onStartRename={setRenameTarget}
      />
      <RenameChatDialog
        target={renameTarget}
        onClose={() => setRenameTarget(null)}
        onRenamed={handleRenamed}
      />
    </>
  )
}

type SessionsRowsProps = {
  sessions: Session[]
  onDelete: (threadId: string) => void
  onStartRename: (session: Session) => void
}

function SessionsRows({ sessions, onDelete, onStartRename }: SessionsRowsProps) {
  const { t } = useTranslation()

  if (sessions.length === 0) {
    return (
      <p className="px-2 py-1 text-xs text-sidebar-foreground/50">
        {t("sidebar.no_sessions")}
      </p>
    )
  }

  return sessions.map((session) => (
    <SessionItem
      key={session.thread_id}
      session={session}
      onDelete={onDelete}
      onStartRename={onStartRename}
    />
  ))
}

type SessionItemProps = {
  session: Session
  onDelete: (threadId: string) => void
  onStartRename: (session: Session) => void
}

function SessionItem({ session, onDelete, onStartRename }: SessionItemProps) {
  const { t, i18n } = useTranslation()
  const navigate = useNavigate()
  const { threadId: activeThreadId } = useParams<{ threadId: string }>()

  const dateFormatter = useMemo(
    () => new Intl.DateTimeFormat(i18n.language === "pt" ? "pt-PT" : "en-GB", {
      dateStyle: "long",
      timeStyle: "short",
    }),
    [i18n.language],
  )

  const formattedDate = dateFormatter.format(new Date(session.created_at))
  const label = session.name ?? formattedDate

  async function handleDelete() {
    await deleteChat(session.thread_id)
    onDelete(session.thread_id)
    if (activeThreadId === session.thread_id) navigate("/chat")
  }

  function handleView() {
    navigate(`/chat/${session.thread_id}`)
  }

  function handleRename() {
    onStartRename(session)
  }

  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        className="text-sidebar-foreground/70 pr-8"
        render={
          <Link to={`/chat/${session.thread_id}`}>
            <span className="truncate">{label}</span>
          </Link>
        }
      />

      <DropdownMenu>
        <SidebarMenuAction
          showOnHover
          render={
            <DropdownMenuTrigger>
              <EllipsisVertical />
            </DropdownMenuTrigger>
          }
        />

        <DropdownMenuContent side="right" align="start">
          <DropdownMenuItem onClick={handleView}>
            <EyeIcon />
            {t("sidebar.view")}
          </DropdownMenuItem>

          <DropdownMenuItem onClick={handleRename}>
            <PencilIcon />
            {t("sidebar.rename")}
          </DropdownMenuItem>

          <DropdownMenuItem variant="destructive" onClick={handleDelete}>
            <Trash2Icon />
            {t("sidebar.delete")}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  )
}

type RenameChatDialogProps = {
  target: Session | null
  onClose: () => void
  onRenamed: (threadId: string, name: string) => void
}

function RenameChatDialog({
  target,
  onClose,
  onRenamed,
}: RenameChatDialogProps) {
  if (!target) return null
  return (
    <RenameChatDialogForm
      key={target.thread_id}
      target={target}
      onClose={onClose}
      onRenamed={onRenamed}
    />
  )
}

type RenameChatDialogFormProps = {
  target: Session
  onClose: () => void
  onRenamed: (threadId: string, name: string) => void
}

function RenameChatDialogForm({
  target,
  onClose,
  onRenamed,
}: RenameChatDialogFormProps) {
  const { t } = useTranslation()
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const renameSchema = z.object({
    name: z
      .string()
      .min(1, t("sidebar.validation.name_required"))
      .max(255, t("sidebar.validation.name_max")),
  })

  const form = useForm<{ name: string }>({
    resolver: zodResolver(renameSchema),
    defaultValues: { name: target.name ?? "" },
  })

  async function handleSubmit(data: { name: string }) {
    setSubmitError(null)
    setIsSubmitting(true)
    try {
      const res = await renameChat(target.thread_id, data.name.trim())
      onRenamed(res.thread_id, res.name)
      onClose()
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : t("sidebar.rename_dialog.error_default"))
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleOpenChange(open: boolean) {
    if (!open) onClose()
  }

  return (
    <Dialog open onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t("sidebar.rename_dialog.title")}</DialogTitle>
          <DialogDescription>
            {t("sidebar.rename_dialog.description")}
          </DialogDescription>
        </DialogHeader>

        <form
          id="rename-chat-form"
          onSubmit={form.handleSubmit(handleSubmit)}
        >
          <FieldGroup>
            <Controller
              name="name"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="rename-chat-name">{t("sidebar.rename_dialog.label")}</FieldLabel>
                  <Input
                    {...field}
                    id="rename-chat-name"
                    autoFocus
                    aria-invalid={fieldState.invalid}
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />
          </FieldGroup>
        </form>

        {submitError && (
          <p className="text-sm text-destructive">{submitError}</p>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isSubmitting}>
            {t("common.cancel")}
          </Button>
          <Button
            type="submit"
            form="rename-chat-form"
            disabled={isSubmitting}
          >
            {isSubmitting ? t("common.saving") : t("common.save")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
