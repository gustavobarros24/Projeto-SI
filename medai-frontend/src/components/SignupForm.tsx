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

export function SignupForm() {
  const { t } = useTranslation()
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const signupSchema = z.object({
    name: z.string().min(1, t("auth.validation.name_required")),
    email: z.email(t("auth.validation.email_invalid")),
    password: z.string().min(6, t("auth.validation.password_min")),
  })

  const form = useForm<{ name: string; email: string; password: string }>({
    resolver: zodResolver(signupSchema),
    defaultValues: { name: "", email: "", password: "" },
  })

  async function handleSubmit(data: { name: string; email: string; password: string }) {
    setError(null)
    setIsLoading(true)

    try {
      await signup(data.name, data.email, data.password)
      navigate("/chat", { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : t("auth.signup.error_default"))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-sm">
      <CardHeader className="text-center">
        <CardTitle className="text-2xl">{t("common.app_name")}</CardTitle>
        <CardDescription>{t("auth.signup.title")}</CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <p className="mb-4 text-sm text-destructive text-center">{error}</p>
        )}
        <form id="signup-form" onSubmit={form.handleSubmit(handleSubmit)}>
          <FieldGroup>
            <Controller
              name="name"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="signup-name">{t("common.name")}</FieldLabel>
                  <Input
                    {...field}
                    id="signup-name"
                    type="text"
                    placeholder={t("auth.placeholders.name")}
                    aria-invalid={fieldState.invalid}
                    autoComplete="name"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />
            <Controller
              name="email"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor="signup-email">{t("common.email")}</FieldLabel>
                  <Input
                    {...field}
                    id="signup-email"
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
                  <FieldLabel htmlFor="signup-password">
                    {t("common.password")}
                  </FieldLabel>
                  <Input
                    {...field}
                    id="signup-password"
                    type="password"
                    placeholder={t("auth.placeholders.password")}
                    aria-invalid={fieldState.invalid}
                    autoComplete="new-password"
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
          form="signup-form"
          className="w-full"
          disabled={isLoading}
        >
          {isLoading ? t("auth.signup.submitting") : t("auth.signup.submit")}
        </Button>
        <p className="text-sm text-center text-muted-foreground">
          {t("auth.signup.has_account")}{" "}
          <Link
            to="/login"
            className="text-primary underline underline-offset-4"
          >
            {t("auth.signup.login_link")}
          </Link>
        </p>
      </CardFooter>
    </Card>
  )
}
