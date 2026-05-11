import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: '../..',
  testMatch: '**/001-lecs-host-management/*.spec.ts',
  fullyParallel: true,
  forbidOnly: false,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['list'], ['html', { outputFolder: '../reports/playwright-report' }]],
  use: {
    baseURL: 'http://localhost:8000',
    trace: 'on-first-retry',
    actionTimeout: 10000,
    navigationTimeout: 15000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
