// tests/fixtures.ts
import { test as base, expect } from "@playwright/test";

// Extend test to log backend errors
export const test = base.extend({
  page: async ({ page }, use) => {
    const errors: Array<{
      url: string;
      status: number;
      statusText: string;
      responseBody?: string;
    }> = [];

    // Monitor API responses for errors
    page.on("response", async (response) => {
      const url = response.url();
      const status = response.status();

      // Log 400/404/422/500 API errors (ignore auth endpoints)
      if (
        url.includes("/api/") &&
        (status === 400 || status === 404 || status === 422 || status === 500)
      ) {
        const isAuth =
          url.includes("/login") ||
          url.includes("/refresh") ||
          url.includes("/auto_login") ||
          url.includes("/logout");
        if (!isAuth) {
          let responseBody: string | undefined;
          try {
            responseBody = await response.text();
          } catch (_e) {
            responseBody = "Could not read response";
          }
          errors.push({
            url,
            status,
            statusText: response.statusText(),
            responseBody,
          });
        }
      }
    });

    await use(page);

    // Summary at end
    if (errors.length > 0) {
    }
  },
});

export { expect };
