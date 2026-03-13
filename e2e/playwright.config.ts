import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for Sefaria Book Creator E2E tests.
 * The Next.js dev server is started automatically when running locally.
 * In CI the server is expected to already be running (see webServer.reuseExistingServer).
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'list',

  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    cwd: '../frontend',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
