import { test, expect } from '@playwright/test';
import { adminCredentials } from '../../fixtures/data/admin-credentials';

test.describe('SC-07: 默认密码首次强制修改', () => {
  test('首次登录后弹出密码修改提示', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await expect(page.locator('[data-testid="password-change-modal"]')).toBeVisible();
  });
});
