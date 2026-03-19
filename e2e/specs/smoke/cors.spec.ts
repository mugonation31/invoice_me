import { test, expect } from "@playwright/test";
import { CorsApi } from "../../pages/cors-api";
import { ALLOWED_ORIGINS, DISALLOWED_ORIGIN } from "../../fixtures/test-data";

/**
 * CORS configuration tests.
 *
 * These tests verify the fix for CORS only allowing port 4200.
 * The Docker frontend runs on port 4201, so the backend must allow
 * both http://localhost:4200 and http://localhost:4201 as origins.
 *
 * The backend config.py defaults:
 *   cors_origins: str = "http://localhost:4200,http://localhost:4201"
 */
test.describe("CORS headers", () => {
  let corsApi: CorsApi;

  test.beforeEach(async ({ request }) => {
    corsApi = new CorsApi(request);
  });

  test("allows requests from localhost:4200 (dev server)", async () => {
    await corsApi.assertOriginAllowed(ALLOWED_ORIGINS[0]);
  });

  test("allows requests from localhost:4201 (Docker frontend)", async () => {
    await corsApi.assertOriginAllowed(ALLOWED_ORIGINS[1]);
  });

  test("preflight from Docker frontend origin returns CORS headers", async () => {
    const response = await corsApi.assertPreflightAllowed(ALLOWED_ORIGINS[1]);
    const allowHeaders =
      response.headers()["access-control-allow-headers"];
    // Authorization header must be allowed for Bearer token auth
    expect(allowHeaders).toBeDefined();
  });

  test("rejects requests from unauthorized origins", async () => {
    await corsApi.assertOriginRejected(DISALLOWED_ORIGIN);
  });

  test("includes credentials support in CORS headers", async () => {
    const response = await corsApi.sendPreflight(
      "/health",
      ALLOWED_ORIGINS[1]
    );
    const allowCredentials =
      response.headers()["access-control-allow-credentials"];
    expect(allowCredentials).toBe("true");
  });
});
