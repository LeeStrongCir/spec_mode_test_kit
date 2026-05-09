import { test, expect } from '@playwright/test';
import { emptyCredentials } from '../../fixtures/data/invalid-credentials';

test.describe('SC-05: 空凭证提交拦截', () => {
  test('用户名空时提交被拦截', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="password-input"]').fill('somepass');
    await page.locator('[data-testid="login-button"]').click();
    await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
  });

  test('密码空时提交被拦截', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill('admin');
    await page.locator('[data-testid="login-button"]').click();
    await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
  });

  test('两者皆空时提交被拦截', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="login-button"]').click();
    await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
  });
});
