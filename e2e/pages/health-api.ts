import { APIRequestContext, expect } from "@playwright/test";
import { backendUrl } from "../utils/api-client";

/**
 * Page object (API object) for the backend health and root endpoints.
 * Encapsulates all selectors/URLs and provides assertion methods.
 */
export class HealthApi {
  constructor(private readonly request: APIRequestContext) {}

  // -- Endpoints --

  private readonly rootPath = "/";
  private readonly healthPath = "/health";

  // -- Actions --

  async getRoot() {
    return this.request.get(backendUrl(this.rootPath));
  }

  async getHealth() {
    return this.request.get(backendUrl(this.healthPath));
  }

  // -- Assertions --

  async assertRootIsReachable() {
    const response = await this.getRoot();
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty("message");
    expect(body.message).toContain("Invoice Me API");
    expect(body).toHaveProperty("version");
    return body;
  }

  async assertHealthIsOk() {
    const response = await this.getHealth();
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body).toHaveProperty("status", "OK");
    return body;
  }
}
