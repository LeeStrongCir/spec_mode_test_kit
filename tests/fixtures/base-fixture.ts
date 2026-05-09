import { test as base } from '@playwright/test';

type Fixtures = {
  loginAsAdmin: () => Promise<void>;
};

export const test = base.extend<Fixtures>({
  loginAsAdmin: async ({ page }, use) => {
    await use(async () => {
      await page.goto('/login');
      await page.locator('[data-testid="username-input"]').fill('admin');
      await page.locator('[data-testid="password-input"]').fill('admin@123');
      await page.locator('[data-testid="login-button"]').click();
      await page.waitForURL('**/console**');
    });
  },
});
