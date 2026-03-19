import { APIRequestContext } from "@playwright/test";

/**
 * Shared constants for the Docker Compose deployment endpoints.
 */
export const BACKEND_URL = "http://localhost:8001";
export const FRONTEND_URL = "http://localhost:4201";

/**
 * Helper to build a full backend URL for a given path.
 */
export function backendUrl(path: string): string {
  return `${BACKEND_URL}${path}`;
}

/**
 * Helper to build a full frontend URL for a given path.
 */
export function frontendUrl(path: string): string {
  return `${FRONTEND_URL}${path}`;
}

/**
 * Sends a preflight OPTIONS request to check CORS headers.
 * Returns the response so callers can assert on headers.
 */
export async function sendCorsPreflight(
  request: APIRequestContext,
  path: string,
  origin: string
) {
  // Playwright's request context does not directly support OPTIONS,
  // so we use fetch to send the preflight manually.
  const response = await request.fetch(backendUrl(path), {
    method: "OPTIONS",
    headers: {
      Origin: origin,
      "Access-Control-Request-Method": "GET",
      "Access-Control-Request-Headers": "Authorization",
    },
  });
  return response;
}
