import { test, expect } from "@playwright/test";
import { AuthApi } from "../../pages/auth-api";
import {
  INVALID_JWT_TOKEN,
  MALFORMED_TOKEN,
  getTestToken,
} from "../../fixtures/test-data";

/**
 * Authentication flow tests.
 *
 * These tests verify the fixes for JWT authentication:
 *   1. PyJWT is installed (replaced python-jose which lacked ES256 support)
 *   2. JWKS fetching works (ca-certificates installed in Docker image)
 *   3. Token validation correctly rejects invalid tokens
 *   4. Token validation correctly accepts valid Supabase tokens
 *
 * Tests that require a valid Supabase token are skipped if
 * no credentials are available in the environment.
 */
test.describe("JWT authentication", () => {
  let authApi: AuthApi;

  test.beforeEach(async ({ request }) => {
    authApi = new AuthApi(request);
  });

  test("rejects requests without authentication token", async () => {
    await authApi.assertUnauthenticatedRejected();
  });

  test("rejects requests with an expired/invalid JWT token", async () => {
    await authApi.assertInvalidTokenRejected(INVALID_JWT_TOKEN);
  });

  test("rejects requests with a malformed token string", async () => {
    await authApi.assertInvalidTokenRejected(MALFORMED_TOKEN);
  });

  test("returns proper WWW-Authenticate header on 401", async () => {
    const response = await authApi.getClientsWithInvalidToken(INVALID_JWT_TOKEN);
    expect(response.status()).toBe(401);
    const wwwAuth = response.headers()["www-authenticate"];
    expect(wwwAuth).toBe("Bearer");
  });

  test("accepts valid Supabase token and returns clients list", async () => {
    const token = await getTestToken();
    test.skip(!token, "No Supabase test credentials -- skipping authenticated test");
    await authApi.assertValidTokenAccepted(token!);
  });

  test("accepts valid token for dashboard endpoint", async () => {
    const token = await getTestToken();
    test.skip(!token, "No Supabase test credentials -- skipping authenticated test");
    await authApi.assertDashboardAccessible(token!);
  });
});
