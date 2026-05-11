import { test, expect } from '@playwright/test';
import { adminCredentials } from '../../fixtures/data/admin-credentials';

/**
 * LECS Host Creation E2E Tests
 * Traceability: spec.md US3 -> tests/cases/.../sc-03-create-host.md
 */

test.describe('SC-03: Create Host', () => {
  async function loginAndGoToCreateForm(page: ReturnType<typeof test>['page']) {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**', { timeout: 5000 });

    await page.goto('/console/lecs-hosts/list');
    await page.waitForURL('**/console/lecs-hosts/list**', { timeout: 5000 });
    await page.locator('[data-testid="create-host-button"]').click();
    await page.waitForURL('**/console/lecs-hosts/create**', { timeout: 5000 });
  }

  async function fillValidForm(page: ReturnType<typeof test>['page']) {
    await page.locator('[data-testid="hostname-input"]').fill('valid01');
    await page.locator('[data-testid="username-input-form"]').fill('admin_01');
    await page.locator('[data-testid="password-input-form"]').fill('Admin@123');
    await page.locator('[data-testid="spec-eco-2c2g"]').click();
    await page.locator('[data-testid="duration-3-months"]').click();
  }

  // TC-020
  test('[TC-020] Navigate from list page to create form, six config sections render', async ({ page }) => {
    await loginAndGoToCreateForm(page);

    const sections = [
      'basic-config-section',
      'instance-spec-section',
      'os-section',
      'ip-config-section',
      'duration-section',
      'cost-section',
    ];

    for (const sectionId of sections) {
      await expect(page.locator(`[data-testid="${sectionId}"]`)).toBeVisible();
    }

    await expect(page.locator('[data-testid="hostname-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="username-input-form"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input-form"]')).toBeVisible();
    await expect(page.locator('[data-testid="purchase-button"]')).toBeVisible();
  });

  // TC-021
  test('[TC-021] Billing mode defaults to 包年/包月, can switch to 按需计费', async ({ page }) => {
    await loginAndGoToCreateForm(page);

    const packageRadio = page.locator('[data-testid="billing-package"]');
    const onDemandRadio = page.locator('[data-testid="billing-on-demand"]');

    await expect(packageRadio).toBeChecked();
    await expect(onDemandRadio).not.toBeChecked();

    await onDemandRadio.click();
    await expect(onDemandRadio).toBeChecked();
    await expect(packageRadio).not.toBeChecked();

    await packageRadio.click();
    await expect(packageRadio).toBeChecked();
    await expect(onDemandRadio).not.toBeChecked();
  });

  // TC-022
  test('[TC-022] Hostname validation - invalid formats show errors, valid passes', async ({ page }) => {
    await loginAndGoToCreateForm(page);

    const hostnameInput = page.locator('[data-testid="hostname-input"]');
    const errorText = page.locator('[data-testid="hostname-error"]');

    await hostnameInput.fill('_invalid');
    await hostnameInput.blur();
    await expect(errorText).toBeVisible();

    await hostnameInput.fill('ab');
    await hostnameInput.blur();
    await expect(errorText).toBeVisible();

    await hostnameInput.fill('abcdefghijklmn');
    await hostnameInput.blur();
    await expect(errorText).toBeVisible();

    await hostnameInput.fill('valid01');
    await hostnameInput.blur();
    await expect(errorText).not.toBeVisible();
  });

  // TC-023
  test('[TC-023] Credential validation - username/password length errors and valid pass', async ({ page }) => {
    await loginAndGoToCreateForm(page);

    const usernameInput = page.locator('[data-testid="username-input-form"]');
    const passwordInput = page.locator('[data-testid="password-input-form"]');
    const usernameError = page.locator('[data-testid="username-error"]');
    const passwordError = page.locator('[data-testid="password-error"]');

    await usernameInput.fill('ab');
    await usernameInput.blur();
    await expect(usernameError).toBeVisible();

    await usernameInput.fill('abcdefghijklmnopq');
    await usernameInput.blur();
    await expect(usernameError).toBeVisible();

    await usernameInput.fill('');
    await expect(usernameError).not.toBeVisible();

    await passwordInput.fill('Ab1');
    await passwordInput.blur();
    await expect(passwordError).toBeVisible();

    await passwordInput.fill('A'.repeat(33) + '1b!');
    await passwordInput.blur();
    await expect(passwordError).toBeVisible();

    await passwordInput.fill('');
    await expect(passwordError).not.toBeVisible();

    await usernameInput.fill('admin_01');
    await usernameInput.blur();
    await expect(usernameError).not.toBeVisible();

    await passwordInput.fill('Admin@123');
    await passwordInput.blur();
    await expect(passwordError).not.toBeVisible();
  });

  // TC-028
  test('[TC-028] Cost estimation updates on spec and billing mode changes', async ({ page }) => {
    await loginAndGoToCreateForm(page);

    const costDisplay = page.locator('[data-testid="cost-total"]');
    const costUnit = page.locator('[data-testid="cost-unit"]');

    await page.locator('[data-testid="billing-package"]').click();
    await page.locator('[data-testid="spec-eco-2c2g"]').click();
    await page.locator('[data-testid="duration-3-months"]').click();

    await expect.poll(async () => (await costDisplay.textContent())?.trim()).toMatch(/\d+/);
    expect(await costDisplay.textContent()).toContain('300');

    await page.locator('[data-testid="billing-on-demand"]').click();
    await expect.poll(async () => (await costUnit.textContent())?.trim()).toContain('元/天');

    await page.locator('[data-testid="spec-eco-2c4g"]').click();
    await expect.poll(async () => (await costDisplay.textContent())?.trim()).toMatch(/\d+/);
    const costText3 = await costDisplay.textContent();
    expect(parseFloat(costText3!)).toBeGreaterThan(3);

    await page.locator('[data-testid="billing-package"]').click();
    await page.locator('[data-testid="spec-eco-4c8g"]').click();

    await expect.poll(async () => (await costDisplay.textContent())?.trim()).toMatch(/\d+/);
    expect(await costDisplay.textContent()).toContain('720');
  });

  // TC-029
  test('[TC-029] Confirmation dialog shows config summary, cancel preserves form, confirm submits', async ({ page }) => {
    await loginAndGoToCreateForm(page);
    await fillValidForm(page);

    await page.locator('[data-testid="purchase-button"]').click();

    const dialog = page.locator('[data-testid="confirm-dialog"]');
    await expect(dialog).toBeVisible();

    await expect(page.locator('[data-testid="dialog-billing-mode"]')).toBeVisible();
    await expect(page.locator('[data-testid="dialog-hostname"]')).toBeVisible();
    await expect(page.locator('[data-testid="dialog-credentials"]')).toBeVisible();
    await expect(page.locator('[data-testid="dialog-spec"]')).toBeVisible();
    await expect(page.locator('[data-testid="dialog-os"]')).toBeVisible();
    await expect(page.locator('[data-testid="dialog-ip-config"]')).toBeVisible();
    await expect(page.locator('[data-testid="dialog-duration"]')).toBeVisible();
    await expect(page.locator('[data-testid="dialog-cost"]')).toBeVisible();

    await page.locator('[data-testid="dialog-cancel"]').click();
    await expect(dialog).not.toBeVisible();

    await expect(page.locator('[data-testid="hostname-input"]')).toHaveValue('valid01');
    await expect(page.locator('[data-testid="username-input-form"]')).toHaveValue('admin_01');
    await expect(page.locator('[data-testid="password-input-form"]')).toHaveValue('Admin@123');

    await page.locator('[data-testid="purchase-button"]').click();
    await expect(dialog).toBeVisible();

    await page.locator('[data-testid="dialog-confirm"]').click();

    await page.waitForURL('**/console/lecs-hosts/list**', { timeout: 10000 });
    await expect(page.locator('[data-testid="success-toast"]')).toBeVisible();
  });

  // TC-030
  test('[TC-030] New host shows 创建中 status, transitions to 正常 or 创建失败', async ({ page }) => {
    await loginAndGoToCreateForm(page);
    await fillValidForm(page);

    await page.locator('[data-testid="purchase-button"]').click();
    await page.locator('[data-testid="confirm-dialog"] [data-testid="dialog-confirm"]').click();

    await page.waitForURL('**/console/lecs-hosts/list**', { timeout: 10000 });

    const hostRow = page.locator('[data-testid="host-row-valid01"]');
    await expect(hostRow).toBeVisible({ timeout: 10000 });

    const statusBadge = hostRow.locator('[data-testid="host-status"]');
    await expect(statusBadge).toContainText('创建中', { timeout: 10000 });

    await expect.poll(
      async () => (await statusBadge.textContent())?.trim(),
      { timeout: 60000, intervals: [3000] }
    ).toMatch(/正常|创建失败/);

    const finalStatus = await statusBadge.textContent();
    expect(finalStatus).toMatch(/正常|创建失败/);

    const actionButtons = hostRow.locator('[data-testid="host-actions"] button');
    await expect(actionButtons.first()).toBeEnabled({ timeout: 10000 });
  });
});
