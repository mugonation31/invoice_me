/**
 * Test data and constants for E2E tests.
 *
 * Authentication is handled automatically via Supabase Auth API.
 * Set these environment variables before running:
 *
 *   SUPABASE_TEST_EMAIL=your-test-user@example.com
 *   SUPABASE_TEST_PASSWORD=your-test-password
 *
 * Or for direct token override:
 *   SUPABASE_TEST_TOKEN=eyJ...
 *
 * Tests that do not require auth (health, CORS) will run without them.
 */

import { getAuthToken } from "../utils/auth-helper";

/** A clearly invalid JWT token for testing rejection */
export const INVALID_JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IlRlc3QiLCJpYXQiOjE1MTYyMzkwMjIsImV4cCI6MTUxNjIzOTAyMn0.invalid_signature_here";

/** A malformed string that is not a JWT at all */
export const MALFORMED_TOKEN = "not-a-jwt-token-at-all";

/** Test client data for database connectivity tests */
export const TEST_CLIENT = {
  name: "E2E Test Client",
  email: "e2e-test@example.com",
  phone: "+1-555-0199",
  address: "123 Test Street, Test City, TC 12345",
};

/** Docker Compose port mappings */
export const PORTS = {
  backend: 8001,
  frontend: 4201,
};

/** Allowed CORS origins (matching backend config.py defaults) */
export const ALLOWED_ORIGINS = [
  "http://localhost:4200",
  "http://localhost:4201",
];

/** A disallowed origin for negative CORS testing */
export const DISALLOWED_ORIGIN = "http://evil-site.com";

/**
 * Get a valid Supabase auth token.
 * Auto-authenticates via Supabase Auth API using SUPABASE_TEST_EMAIL/PASSWORD,
 * or falls back to SUPABASE_TEST_TOKEN if set directly.
 * Returns undefined if no credentials are available.
 */
export async function getTestToken(): Promise<string | undefined> {
  return getAuthToken();
}
