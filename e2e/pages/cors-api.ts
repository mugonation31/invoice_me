import { APIRequestContext, expect } from "@playwright/test";
import { backendUrl } from "../utils/api-client";

/**
 * Page object (API object) for verifying CORS configuration.
 * Tests that the backend returns correct CORS headers for allowed origins.
 */
export class CorsApi {
  constructor(private readonly request: APIRequestContext) {}

  // -- Endpoints --

  private readonly healthPath = "/health";

  // -- Actions --

  /**
   * Send a GET request with an Origin header to trigger CORS response headers.
   */
  async getWithOrigin(path: string, origin: string) {
    return this.request.get(backendUrl(path), {
      headers: {
        Origin: origin,
      },
    });
  }

  /**
   * Send an OPTIONS preflight request.
   */
  async sendPreflight(path: string, origin: string) {
    return this.request.fetch(backendUrl(path), {
      method: "OPTIONS",
      headers: {
        Origin: origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Authorization",
      },
    });
  }

  // -- Assertions --

  /**
   * Assert that a given origin receives proper CORS allow headers.
   */
  async assertOriginAllowed(origin: string) {
    const response = await this.getWithOrigin(this.healthPath, origin);
    expect(response.status()).toBe(200);

    const allowOrigin = response.headers()["access-control-allow-origin"];
    expect(allowOrigin).toBe(origin);
    return response;
  }

  /**
   * Assert that preflight for an allowed origin returns correct headers.
   */
  async assertPreflightAllowed(origin: string) {
    const response = await this.sendPreflight(this.healthPath, origin);
    // FastAPI CORS middleware returns 200 for preflight
    expect(response.status()).toBe(200);

    const allowOrigin = response.headers()["access-control-allow-origin"];
    expect(allowOrigin).toBe(origin);

    const allowMethods = response.headers()["access-control-allow-methods"];
    expect(allowMethods).toBeDefined();
    return response;
  }

  /**
   * Assert that a disallowed origin does NOT receive CORS allow headers.
   */
  async assertOriginRejected(origin: string) {
    const response = await this.getWithOrigin(this.healthPath, origin);
    // The endpoint still responds (CORS is browser-enforced),
    // but Access-Control-Allow-Origin should not match the origin.
    const allowOrigin = response.headers()["access-control-allow-origin"];
    expect(allowOrigin).not.toBe(origin);
    return response;
  }
}
