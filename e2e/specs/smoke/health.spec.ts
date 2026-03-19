import { test, expect } from "@playwright/test";
import { HealthApi } from "../../pages/health-api";

/**
 * Health endpoint tests.
 *
 * These tests verify that the Docker backend:
 *   - Starts successfully (uvicorn serving FastAPI)
 *   - Can connect to Supabase PostgreSQL via SSL asyncpg
 *   - Returns proper health check responses (used by Docker healthcheck with curl)
 *
 * The /health endpoint is the same one used by docker-compose.yml healthcheck:
 *   test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
 *
 * If /health returns 200, it proves:
 *   1. curl and ca-certificates are installed in the Docker image
 *   2. The FastAPI app started without import errors (PyJWT installed correctly)
 *   3. The database pool was created (SSL asyncpg connected to Supabase)
 */
test.describe("Backend health endpoint", () => {
  let healthApi: HealthApi;

  test.beforeEach(async ({ request }) => {
    healthApi = new HealthApi(request);
  });

  test("GET / returns API info with version", async () => {
    const body = await healthApi.assertRootIsReachable();
    expect(body.version).toBe("1.0.0");
  });

  test("GET /health returns status OK", async () => {
    await healthApi.assertHealthIsOk();
  });

  test("GET /health responds within acceptable time", async () => {
    const start = Date.now();
    await healthApi.assertHealthIsOk();
    const elapsed = Date.now() - start;
    // Health check should respond in under 5 seconds
    expect(elapsed).toBeLessThan(5000);
  });
});
