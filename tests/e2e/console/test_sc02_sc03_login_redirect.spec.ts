import { test, expect } from '@playwright/test';
import { adminCredentials } from '../../fixtures/data/admin-credentials';

test.describe('SC-02+SC-03: 管理员登录与页面跳转', () => {
  test('admin/admin@123 认证成功并跳转至控制台页面', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**', { timeout: 5000 });
    await expect(page).toHaveURL(/console/);
  });

  test('登录后 URL 路径变为 /console', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await expect(page).toHaveURL(/console/);
  });
});
