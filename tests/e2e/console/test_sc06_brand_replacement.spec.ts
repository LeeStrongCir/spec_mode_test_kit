import { test, expect } from '@playwright/test';
import { adminCredentials } from '../../fixtures/data/admin-credentials';

test.describe('SC-06: 品牌文案全量替换验证', () => {
  test('页面中不存在"华为云"残存文案', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
    const bodyText = await page.locator('body').innerText();
    expect(bodyText).not.toContain('华为云');
  });

  test('Logo 区域显示"Lee云"', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
    await expect(page.locator('[data-testid="logo"]')).toContainText('Lee云');
  });

  test('页面标题包含"Lee云"', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
    await expect(page).toHaveTitle(/Lee云/);
  });

  test('页脚显示"© Lee云"', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
    await expect(page.locator('[data-testid="footer"]')).toContainText('Lee云');
  });

  test('欢迎文案显示"欢迎来到Lee云"', async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
    await expect(page.locator('[data-testid="welcome-message"]')).toContainText('Lee云');
  });
});
