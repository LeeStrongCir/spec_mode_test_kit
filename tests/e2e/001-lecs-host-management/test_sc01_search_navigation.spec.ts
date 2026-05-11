import { test, expect } from '@playwright/test';
import { adminCredentials } from '../../fixtures/data/admin-credentials';

test.describe('SC-01: Search Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**');
  });

  test('TC-001: Input "LECS" in search bar, verify "LECS主机" appears in dropdown with keyword highlighting', async ({ page }) => {
    const searchBar = page.locator('[data-testid="search-bar"]');
    await searchBar.click();
    await searchBar.fill('LECS');

    const dropdown = page.locator('[data-testid="search-results"]');
    await expect(dropdown).toBeVisible();

    const lecsHostItem = dropdown.locator('text=LECS主机').first();
    await expect(lecsHostItem).toBeVisible();

    const highlightedText = dropdown.locator('mark, .highlight, [style*="background"], strong').filter({ hasText: /LECS/i }).first();
    await expect(highlightedText).toBeVisible();
  });

  test('TC-002: Input "云服" in search bar, verify "LECS主机" appears in dropdown with keyword highlighting', async ({ page }) => {
    const searchBar = page.locator('[data-testid="search-bar"]');
    await searchBar.click();
    await searchBar.fill('云服');

    const dropdown = page.locator('[data-testid="search-results"]');
    await expect(dropdown).toBeVisible();

    const lecsHostItem = dropdown.locator('text=LECS主机').first();
    await expect(lecsHostItem).toBeVisible();

    const highlightedText = dropdown.locator('mark, .highlight, [style*="background"], strong').filter({ hasText: /云服/ }).first();
    await expect(highlightedText).toBeVisible();
  });

  test('TC-003: Click search result "LECS主机", verify navigation to /console/lecs-hosts/list', async ({ page }) => {
    const searchBar = page.locator('[data-testid="search-bar"]');
    await searchBar.click();
    await searchBar.fill('LECS');

    const dropdown = page.locator('[data-testid="search-results"]');
    await expect(dropdown).toBeVisible();

    const lecsHostItem = dropdown.locator('text=LECS主机').first();
    await lecsHostItem.click();

    await expect(page).toHaveURL(/\/console\/lecs-hosts\/list/);

    await page.waitForLoadState('networkidle');

    const pageTitle = page.locator('text=LECS主机, text=主机列表').first();
    await expect(pageTitle).toBeVisible({ timeout: 5000 }).catch(async () => {
      const createButton = page.locator('text=创建LECS主机');
      await expect(createButton).toBeVisible({ timeout: 5000 });
    });

    const tableArea = page.locator('[data-testid="host-table"], table, text=暂无数据').first();
    await expect(tableArea).toBeVisible({ timeout: 5000 });
  });
});
