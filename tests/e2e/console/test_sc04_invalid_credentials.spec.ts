import { test, expect } from '@playwright/test';
import { invalidCredentials } from '../../fixtures/data/invalid-credentials';

test.describe('SC-04: 无效凭证登录拒绝', () => {
  test('错误用户名时认证失败并停留在登录页', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(invalidCredentials.wrongUsername.username);
    await page.locator('[data-testid="password-input"]').fill(invalidCredentials.wrongUsername.password);
    await page.locator('[data-testid="login-button"]').click();
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page).not.toHaveURL(/console/);
  });

  test('错误密码时认证失败并停留在登录页', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(invalidCredentials.wrongPassword.username);
    await page.locator('[data-testid="password-input"]').fill(invalidCredentials.wrongPassword.password);
    await page.locator('[data-testid="login-button"]').click();
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });

  test('用户名密码均错误时认证失败', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(invalidCredentials.bothWrong.username);
    await page.locator('[data-testid="password-input"]').fill(invalidCredentials.bothWrong.password);
    await page.locator('[data-testid="login-button"]').click();
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });
});
