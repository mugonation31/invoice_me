import { defineConfig } from "@playwright/test";

/**
 * Playwright configuration for Invoice Me E2E tests.
 *
 * These tests run against the Docker Compose deployment:
 *   - Backend (FastAPI): http://localhost:8001
 *   - Frontend (Angular/nginx): http://localhost:4201
 *
 * Start Docker Compose before running tests:
 *   docker compose up -d --build
 *
 * Run tests:
 *   npx playwright test
 */
export default defineConfig({
  testDir: "./e2e/specs",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never" }]],

  use: {
    /* Base URL for API tests */
    baseURL: "http://localhost:8001",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },

  /* Timeout settings */
  timeout: 30_000,
  expect: {
    timeout: 5_000,
  },

  projects: [
    {
      name: "docker-integration",
      testDir: "./e2e/specs/smoke",
    },
  ],
});
