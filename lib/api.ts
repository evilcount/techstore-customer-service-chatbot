const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit = {},
  demoPassword?: string,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(demoPassword ? { "X-Demo-Password": demoPassword } : {}),
      ...(options.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

export function validateDemoPassword(password: string) {
  return request<{ ok: boolean }>("/api/auth/demo", {
    method: "POST",
    body: JSON.stringify({ password }),
  });
}

export function createSession(customerEmail: string, demoPassword: string) {
  return request<{ session_id: string; customer_email: string }>(
    "/api/chat/sessions",
    {
      method: "POST",
      body: JSON.stringify({ customer_email: customerEmail }),
    },
    demoPassword,
  );
}

export function sendMessage(sessionId: string, message: string, demoPassword: string) {
  return request<{ session_id: string; assistant_message: string; created_at: string }>(
    `/api/chat/sessions/${sessionId}/messages`,
    {
      method: "POST",
      body: JSON.stringify({ message }),
    },
    demoPassword,
  );
}
