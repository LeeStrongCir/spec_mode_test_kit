import { test, expect } from '@playwright/test';
import { adminCredentials } from '../../fixtures/data/admin-credentials';

test.describe('SC-09: 控制台页顶部搜索功能', () => {
  test('输入关键词搜索后结果页面正确加载', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
    await page.locator('[data-testid="search-bar"]').fill('ECS');
    await page.locator('[data-testid="search-bar"]').press('Enter');
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
  });
});
