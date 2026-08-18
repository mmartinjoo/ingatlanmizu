export class ApiError extends Error {
  constructor(
    message: string,
    options: { status?: number; cause?: unknown } = {},
  ) {
    super(message, { cause: options.cause })
    this.name = 'ApiError'
    this.status = options.status
  }

  readonly status?: number
}

export async function get<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  const url = new URL(path, window.location.origin)
  for (const [key, value] of Object.entries(params)) {
    url.searchParams.set(key, value)
  }

  let response: Response
  try {
    response = await fetch(url)
  } catch (cause) {
    // Network-level failure: API down, or CORS rejected the request.
    throw new ApiError(`Nem sikerült elérni az API-t (${url.origin}).`, { cause })
  }

  if (!response.ok) {
    throw new ApiError(`Az API ${response.status} hibával válaszolt.`, { status: response.status })
  }

  return (await response.json()) as T
}
