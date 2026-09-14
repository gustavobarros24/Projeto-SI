import { useState } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { Controller, useForm } from "react-hook-form"
import { Link, useNavigate } from "react-router"
import * as z from "zod"
import { useTranslation } from "react-i18next"

import { useAuth } from "@/contexts/AuthContext"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"

export function LoginForm() {
  const { t } = useTranslation()
  const { login } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const loginSchema = z.object({
    email: z.email(t("auth.validation.email_invalid")),
    password: z.string().min(1, t("auth.validation.password_required")),
  })

  const form = useForm<{ email: string; password: string }>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  })

  async function handleSubmit(data: { email: string; password: string }) {
    setError(null)
    setIsLoading(true)

    try {
      await login(data.email, data.password)
      navigate("/chat", { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : t("auth.login.error_default"))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">{t("common.app_name")}</CardTitle>
        <CardDescription>{t("auth.login.title")}</CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <p className="mb-4 text-sm text-destructive text-center">{error}</p>
        )}
        <form id="login-form" onSubmit={form.handleSubmit(handleSubmit)}>
          <FieldGroup>
            <Controller
              name="email"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="login-email">{t("common.email")}</FieldLabel>
                  <Input
                    {...field}
                    id="login-email"
                    type="email"
                    placeholder={t("auth.placeholders.email")}
                    aria-invalid={fieldState.invalid}
                    autoComplete="email"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />
            <Controller
              name="password"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="login-password">
                    {t("common.password")}
                  </FieldLabel>
                  <Input
                    {...field}
                    id="login-password"
                    type="password"
                    placeholder={t("auth.placeholders.password")}
                    aria-invalid={fieldState.invalid}
                    autoComplete="current-password"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />
          </FieldGroup>
        </form>
      </CardContent>
      <CardFooter className="flex flex-col gap-4">
        <Button
          type="submit"
          form="login-form"
          className="w-full"
          disabled={isLoading}
        >
          {isLoading ? t("auth.login.submitting") : t("auth.login.submit")}
        </Button>
        <p className="text-sm text-center text-muted-foreground">
          {t("auth.login.no_account")}{" "}
          <Link
            to="/signup"
            className="text-primary underline underline-offset-4"
          >
            {t("auth.login.signup_link")}
          </Link>
        </p>
      </CardFooter>
    </Card>
  )
}
