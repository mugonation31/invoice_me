import { test, expect } from "@playwright/test";
import { DatabaseApi } from "../../pages/database-api";
import { TEST_CLIENT, getTestToken } from "../../fixtures/test-data";

/**
 * Database connectivity tests.
 *
 * These tests verify that the SSL asyncpg connection to Supabase works
 * correctly through the Docker backend. They test the full round-trip:
 *   1. Create a record (INSERT via SSL connection)
 *   2. Read the record back (SELECT via SSL connection)
 *   3. Delete the record (DELETE via SSL connection, also cleanup)
 *
 * Credentials are obtained automatically via Supabase Auth API.
 * Set SUPABASE_TEST_EMAIL and SUPABASE_TEST_PASSWORD in the environment.
 */
test.describe("Database connectivity via Supabase SSL", () => {
  let dbApi: DatabaseApi;
  let token: string;

  test.beforeEach(async ({ request }) => {
    dbApi = new DatabaseApi(request);
    const t = await getTestToken();
    test.skip(!t, "No Supabase test credentials -- skipping database test");
    token = t!;
  });

  test("can read clients list from Supabase (proves SSL read works)", async () => {
    await dbApi.assertClientsListable(token);
  });

  test("can create a client in Supabase (proves SSL write works)", async () => {
    const created = await dbApi.assertClientCreated(token, TEST_CLIENT);
    expect(created.id).toBeDefined();
    expect(created.name).toBe(TEST_CLIENT.name);
    expect(created.email).toBe(TEST_CLIENT.email);

    // Cleanup
    await dbApi.assertClientDeleted(token, created.id);
  });

  test("can read back a created client by ID (proves SSL round-trip)", async () => {
    const created = await dbApi.assertClientCreated(token, {
      name: "E2E Roundtrip Client",
      email: "roundtrip@example.com",
    });

    const fetched = await dbApi.assertClientFetchable(token, created.id);
    expect(fetched.name).toBe("E2E Roundtrip Client");
    expect(fetched.email).toBe("roundtrip@example.com");

    // Cleanup
    await dbApi.assertClientDeleted(token, created.id);
  });

  test("returns 404 for non-existent client ID", async () => {
    const fakeId = "00000000-0000-0000-0000-000000000000";
    const response = await dbApi.getClient(token, fakeId);
    expect(response.status()).toBe(404);
  });

  test("can delete a client from Supabase (proves SSL delete works)", async () => {
    const created = await dbApi.assertClientCreated(token, {
      name: "E2E Delete Test",
      email: "delete-test@example.com",
    });

    await dbApi.assertClientDeleted(token, created.id);

    const response = await dbApi.getClient(token, created.id);
    expect(response.status()).toBe(404);
  });
});
