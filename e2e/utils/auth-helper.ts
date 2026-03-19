/**
 * Authenticates against Supabase Auth API to obtain a valid JWT token.
 *
 * Requires environment variables:
 *   SUPABASE_TEST_EMAIL    - email of a test user already registered in your Supabase project
 *   SUPABASE_TEST_PASSWORD - password for that test user
 *
 * Uses the Supabase project URL and anon key from the frontend environment config.
 */

const SUPABASE_URL = "https://iojtyiqceeirgizjmszm.supabase.co";
const SUPABASE_ANON_KEY = "sb_publishable_J6ia-QNdzcfv00pXEno6Bg_Md7gsd_H";

let cachedToken: string | undefined;

/**
 * Sign in with email/password via Supabase GoTrue REST API and return the access token.
 * Caches the token for the duration of the test run.
 */
export async function getAuthToken(): Promise<string | undefined> {
  // Allow direct token override (backwards compatible)
  if (process.env.SUPABASE_TEST_TOKEN) {
    return process.env.SUPABASE_TEST_TOKEN;
  }

  if (cachedToken) {
    return cachedToken;
  }

  const email = process.env.SUPABASE_TEST_EMAIL;
  const password = process.env.SUPABASE_TEST_PASSWORD;

  if (!email || !password) {
    return undefined;
  }

  const response = await fetch(
    `${SUPABASE_URL}/auth/v1/token?grant_type=password`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: SUPABASE_ANON_KEY,
      },
      body: JSON.stringify({ email, password }),
    }
  );

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Supabase auth failed (${response.status}): ${err}`);
  }

  const data = await response.json();
  cachedToken = data.access_token;
  return cachedToken;
}
