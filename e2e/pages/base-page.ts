import { Page, expect } from "@playwright/test";

/**
 * Base page object providing common helpers for all pages.
 * Other page objects should extend this class.
 */
export class BasePage {
  constructor(protected readonly page: Page) {}

  /**
   * Navigate to a path relative to the frontend base URL.
   */
  async navigateTo(path: string) {
    await this.page.goto(`http://localhost:4201${path}`);
  }

  /**
   * Assert the page has loaded without critical console errors.
   * Collects console messages during page load and checks for errors.
   */
  async assertNoConsoleErrors() {
    const errors: string[] = [];
    this.page.on("console", (msg) => {
      if (msg.type() === "error") {
        errors.push(msg.text());
      }
    });
    // Give a moment for any pending console messages
    await this.page.waitForLoadState("networkidle");
    // Filter out common benign errors (e.g. favicon 404)
    const criticalErrors = errors.filter(
      (e) => !e.includes("favicon") && !e.includes("404")
    );
    expect(criticalErrors).toHaveLength(0);
  }

  /**
   * Take a screenshot for debugging purposes.
   */
  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `e2e/screenshots/${name}.png` });
  }
}
