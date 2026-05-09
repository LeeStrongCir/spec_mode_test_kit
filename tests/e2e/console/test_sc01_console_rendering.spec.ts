import { test, expect } from '@playwright/test';
import { adminCredentials } from '../../fixtures/data/admin-credentials';

test.describe('SC-01: 控制台页面渲染展示', () => {
  test('控制台页面所有关键组件均正确渲染', async ({ page }) => {
    // 模拟登录
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    
    await page.waitForURL('**/console**', { timeout: 5000 });
    
    expect(await page.locator('[data-testid="logo"]').isVisible
    expect(await page.locator('[data-testid="topbar"]').isVisible()).toBe(true);
    expect(await page.locator('[data-testid="search-bar"]').isVisible()).toBe(true);
    expect(await page.locator('[data-testid="nav-menu"]').isVisible()).toBe(true);
    expect(await page.locator('[data-testid="tabs"]').isVisible()).toBe(true);
    expect(await page.locator('[data-testid="overview-cards"]').isVisible()).toBe(true);
    expect(await page.locator('[data-testid="service-view"]').isVisible()).toBe(true);
    expect(await page.locator('[data-testid="panels"]').isVisible()).toBe(true);
    expect(await page.locator('[data-testid="footer"]').isVisible()).toBe(true);
  });

  test('控制台页面加载无 JavaScript 错误', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
    await page.waitForLoadState('networkidle');
    
    expect(errors.length).toBe(0);
  });
});
