import { test as base, expect, type Page } from '@playwright/test';
import { adminCredentials } from '../../../fixtures/data/admin-credentials';

type LecsHostFixtures = {
  authenticatedPage: Page;
  populatedListPage: Page;
};

async function loginAsAdmin(page: Page) {
  await page.goto('/login');
  await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
  await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
  await page.locator('[data-testid="login-button"]').click();
  await page.waitForURL('**/console**', { timeout: 5000 });
}

export const test = base.extend<LecsHostFixtures>({
  authenticatedPage: async ({ page }, use) => {
    await loginAsAdmin(page);
    await use(page);
  },
  populatedListPage: async ({ authenticatedPage }, use) => {
    await authenticatedPage.goto('/console/lecs-hosts/list');
    await expect(authenticatedPage.locator('[data-testid="host-list-table"]')).toBeVisible({ timeout: 10000 });
    await use(authenticatedPage);
  },
});

export { expect } from '@playwright/test';
