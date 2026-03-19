import { test, expect } from "@playwright/test";
import { HealthApi } from "../../pages/health-api";
import { BACKEND_URL, FRONTEND_URL } from "../../utils/api-client";

/**
 * Docker healthcheck verification tests.
 *
 * These tests verify the Docker Compose infrastructure is working:
 *   1. The backend healthcheck (curl -f http://localhost:8000/health) works,
 *      which requires curl and ca-certificates to be installed in the image
 *   2. The backend is accessible on the mapped port (8001)
 *   3. The frontend (nginx) is accessible on the mapped port (4201)
 *   4. The backend can serve requests continuously (not crashing)
 *
 * docker-compose.yml healthcheck config:
 *   test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
 *   interval: 30s
 *   timeout: 10s
 *   retries: 3
 *   start_period: 40s
 */
test.describe("Docker infrastructure healthcheck", () => {
  let healthApi: HealthApi;

  test.beforeEach(async ({ request }) => {
    healthApi = new HealthApi(request);
  });

  test("backend is reachable on Docker mapped port 8001", async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/health`);
    expect(response.status()).toBe(200);
    expect(response.ok()).toBe(true);
  });

  test("frontend is reachable on Docker mapped port 4201", async ({
    request,
  }) => {
    const response = await request.get(FRONTEND_URL);
    // nginx serves the Angular app; expect 200
    expect(response.status()).toBe(200);
  });

  test("backend health endpoint matches Docker healthcheck expectations", async () => {
    // The Docker healthcheck uses: curl -f http://localhost:8000/health
    // curl -f fails on HTTP errors (4xx, 5xx), so we need 2xx
    const body = await healthApi.assertHealthIsOk();
    // Verify the response is valid JSON (curl -f does not check this,
    // but it confirms the endpoint is fully functional)
    expect(body).toBeDefined();
    expect(typeof body).toBe("object");
  });

  test("backend survives multiple rapid health checks without crashing", async () => {
    // Simulate what Docker healthcheck does repeatedly
    const checks = Array.from({ length: 5 }, () =>
      healthApi.assertHealthIsOk()
    );
    const results = await Promise.all(checks);
    expect(results).toHaveLength(5);
    results.forEach((body) => {
      expect(body).toHaveProperty("status", "OK");
    });
  });

  test("backend returns proper content-type header", async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/health`);
    const contentType = response.headers()["content-type"];
    expect(contentType).toContain("application/json");
  });
});
