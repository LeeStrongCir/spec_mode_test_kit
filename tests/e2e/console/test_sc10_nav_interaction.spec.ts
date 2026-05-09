import { test, expect } from '@playwright/test';
import { adminCredentials } from '../../fixtures/data/admin-credentials';

test.describe('SC-10: 控制台页导航栏交互', () => {
  test('点击"备案"菜单跳转至备案页面', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
    await page.locator('[data-testid="nav-beian"]').click();
    await expect(page).toHaveURL(/beian/);
  });

  test('点击"资源"菜单跳转至资源页面', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
    await page.locator('[data-testid="nav-resources"]').click();
    await expect(page).toHaveURL(/resources/);
  });
});
