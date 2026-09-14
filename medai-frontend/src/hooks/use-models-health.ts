import { useQuery } from "@tanstack/react-query"
import { checkModelsHealth } from "@/lib/api"

export type ModelsHealthStatus = "loading" | "ok" | "error"

const POLL_INTERVAL_MS = 30_000

export function useModelsHealth(): {
  status: ModelsHealthStatus
  message: string
} {
  const { data, isPending, isError } = useQuery({
    queryKey: ["models-health"],
    queryFn: checkModelsHealth,
    refetchInterval: POLL_INTERVAL_MS,
    refetchOnWindowFocus: true,
    retry: false,
    staleTime: 0,
  })

  if (isPending) {
    return { status: "loading", message: "A verificar modelos..." }
  }

  if (isError) {
    return {
      status: "error",
      message: "Não foi possível contactar o servidor.",
    }
  }

  return { status: data.status, message: data.message }
}
