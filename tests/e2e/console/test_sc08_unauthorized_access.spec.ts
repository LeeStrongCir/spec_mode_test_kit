import { test, expect } from '@playwright/test';

test.describe('SC-08: 控制台页未登录直接访问拦截', () => {
  test('未登录时直接访问 /console 被重定向至登录页', async ({ page }) => {
    await page.goto('/console');
    await expect(page).toHaveURL(/login/);
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });
});
