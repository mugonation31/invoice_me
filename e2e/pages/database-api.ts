import { APIRequestContext, expect } from "@playwright/test";
import { backendUrl } from "../utils/api-client";

/**
 * Page object (API object) for verifying database connectivity through Supabase.
 * Tests that the SSL asyncpg connection to Supabase works correctly.
 */
export class DatabaseApi {
  constructor(private readonly request: APIRequestContext) {}

  // -- Endpoints --

  private readonly clientsPath = "/api/clients";

  // -- Actions --

  /**
   * Create a new client via POST /api/clients.
   */
  async createClient(
    token: string,
    data: { name: string; email: string; phone?: string; address?: string }
  ) {
    return this.request.post(backendUrl(this.clientsPath), {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      data,
    });
  }

  /**
   * List all clients via GET /api/clients.
   */
  async listClients(token: string) {
    return this.request.get(backendUrl(this.clientsPath), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  /**
   * Get a single client by ID.
   */
  async getClient(token: string, clientId: string) {
    return this.request.get(backendUrl(`${this.clientsPath}/${clientId}`), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  /**
   * Delete a client by ID.
   */
  async deleteClient(token: string, clientId: string) {
    return this.request.delete(backendUrl(`${this.clientsPath}/${clientId}`), {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  // -- Assertions --

  /**
   * Assert that a client can be created and returned with correct data.
   * This proves the SSL asyncpg connection to Supabase works for writes.
   */
  async assertClientCreated(
    token: string,
    data: { name: string; email: string; phone?: string; address?: string }
  ) {
    const response = await this.createClient(token, data);
    expect(response.status()).toBe(201);
    const body = await response.json();
    expect(body).toHaveProperty("id");
    expect(body.name).toBe(data.name);
    expect(body.email).toBe(data.email);
    return body;
  }

  /**
   * Assert that clients can be listed.
   * This proves the SSL asyncpg connection to Supabase works for reads.
   */
  async assertClientsListable(token: string) {
    const response = await this.listClients(token);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(Array.isArray(body)).toBe(true);
    return body;
  }

  /**
   * Assert that a specific client can be fetched by ID.
   */
  async assertClientFetchable(token: string, clientId: string) {
    const response = await this.getClient(token, clientId);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty("id", clientId);
    return body;
  }

  /**
   * Assert that a client can be deleted.
   */
  async assertClientDeleted(token: string, clientId: string) {
    const response = await this.deleteClient(token, clientId);
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty("message");
    return body;
  }
}
