import { APIRequestContext, expect } from "@playwright/test";
import { backendUrl } from "../utils/api-client";

/**
 * Page object (API object) for verifying authentication behavior.
 * Tests that JWT token validation works correctly with PyJWT.
 */
export class AuthApi {
  constructor(private readonly request: APIRequestContext) {}

  // -- Endpoints (protected routes requiring Bearer token) --

  private readonly clientsPath = "/api/clients";
  private readonly dashboardPath = "/api/dashboard";

  // -- Actions --

  /**
   * Attempt to access a protected endpoint without any auth token.
   */
  async getClientsWithoutAuth() {
    return this.request.get(backendUrl(this.clientsPath));
  }

  /**
   * Attempt to access a protected endpoint with an invalid/expired token.
   */
  async getClientsWithInvalidToken(token: string) {
    return this.request.get(backendUrl(this.clientsPath), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  /**
   * Attempt to access a protected endpoint with a valid auth token.
   */
  async getClientsWithToken(token: string) {
    return this.request.get(backendUrl(this.clientsPath), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  /**
   * Access the dashboard endpoint with a valid auth token.
   */
  async getDashboardWithToken(token: string) {
    return this.request.get(backendUrl(this.dashboardPath), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  // -- Assertions --

  /**
   * Assert that unauthenticated requests are rejected with 401 or 403.
   */
  async assertUnauthenticatedRejected() {
    const response = await this.getClientsWithoutAuth();
    // FastAPI HTTPBearer returns 403 when no credentials are provided
    expect([401, 403]).toContain(response.status());
    return response;
  }

  /**
   * Assert that an invalid token is rejected with 401.
   */
  async assertInvalidTokenRejected(token: string) {
    const response = await this.getClientsWithInvalidToken(token);
    expect(response.status()).toBe(401);
    const body = await response.json();
    expect(body).toHaveProperty("detail");
    expect(body.detail).toContain("Invalid authentication credentials");
    return response;
  }

  /**
   * Assert that a valid token grants access (200 response).
   */
  async assertValidTokenAccepted(token: string) {
    const response = await this.getClientsWithToken(token);
    expect(response.status()).toBe(200);
    const body = await response.json();
    // Should return an array of clients (possibly empty)
    expect(Array.isArray(body)).toBe(true);
    return body;
  }

  /**
   * Assert that dashboard returns proper structure with a valid token.
   */
  async assertDashboardAccessible(token: string) {
    const response = await this.getDashboardWithToken(token);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty("total_clients");
    expect(body).toHaveProperty("total_invoices");
    expect(body).toHaveProperty("total_revenue");
    return body;
  }
}
