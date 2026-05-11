import { test, expect } from '@playwright/test';
import { adminCredentials } from '../../fixtures/data/admin-credentials';

test.describe('SC-05: Safe Delete', () => {

  // Shared helpers
  async function loginAndNavigate(page) {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill(adminCredentials.username);
    await page.locator('[data-testid="password-input"]').fill(adminCredentials.password);
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console/lecs-hosts/list**');
  }

  async function findHostRowByStatus(page, statusText) {
    const rows = page.locator('[data-testid="host-table"] tbody tr');
    const count = await rows.count();
    for (let i = 0; i < count; i++) {
      const row = rows.nth(i);
      const statusCell = row.locator('[data-testid="host-status"]');
      const text = await statusCell.textContent();
      if (text?.includes(statusText)) {
        return row;
      }
    }
    return null;
  }

  async function getQuotaCount(page) {
    const quotaText = await page.locator('[data-testid="quota-count"]').textContent();
    const match = quotaText?.match(/(\d+)\s*\/\s*\d+/);
    return match ? parseInt(match[1], 10) : -1;
  }

  async function waitForRowDisappearance(page, getHostId) {
    await expect.poll(async () => {
      const rows = page.locator('[data-testid="host-table"] tbody tr');
      const count = await rows.count();
      for (let i = 0; i < count; i++) {
        const row = rows.nth(i);
        const id = await row.getAttribute('data-host-id');
        if (id === getHostId()) return true;
      }
      return false;
    }).toBe(false, { timeout: 10000 });
  }

  async function confirmDialogAndDelete(page) {
    const confirmButton = page.locator('[data-testid="confirm-dialog-confirm"]');
    await expect(confirmButton).toBeVisible();
    await confirmButton.click();
  }

  async function cancelDialog(page) {
    const cancelButton = page.locator('[data-testid="confirm-dialog-cancel"]');
    await expect(cancelButton).toBeVisible();
    await cancelButton.click();
  }

  // TC-050: Verify running host delete interception
  test('TC-050: 验证运行态主机删除拦截', async ({ page }) => {
    await loginAndNavigate(page);

    // Step 1: Verify "正常" status host delete button is disabled
    const normalRow = await findHostRowByStatus(page, '正常');
    expect(normalRow).not.toBeNull();

    const deleteBtn = normalRow.locator('[data-testid="delete-button"]');
    await expect(deleteBtn).toBeDisabled();

    // Step 2: Defensive check - if button is somehow clickable, verify interception
    const isDisabled = await deleteBtn.isDisabled();
    if (!isDisabled) {
      await deleteBtn.click();
      const toast = page.locator('[data-testid="toast-message"]');
      await expect(toast).toContainText('请先将主机关机，再执行删除操作');
    }

    // Step 3: Verify "创建中" status host delete button is disabled or intercepted
    const creatingRow = await findHostRowByStatus(page, '创建中');
    if (creatingRow) {
      const creatingDeleteBtn = creatingRow.locator('[data-testid="delete-button"]');
      const isCreatingDisabled = await creatingDeleteBtn.isDisabled();
      expect(isCreatingDisabled).toBe(true);
    }

    // Step 4: Verify "关机中" status host delete button is disabled or intercepted
    const stoppingRow = await findHostRowByStatus(page, '关机中');
    if (stoppingRow) {
      const stoppingDeleteBtn = stoppingRow.locator('[data-testid="delete-button"]');
      const isStoppingDisabled = await stoppingDeleteBtn.isDisabled();
      expect(isStoppingDisabled).toBe(true);
    }
  });

  // TC-051: Stopped host deletion flow
  test('TC-051: 验证已关机主机的删除流程', async ({ page }) => {
    await loginAndNavigate(page);

    // Record initial quota
    const initialQuota = await getQuotaCount(page);

    // Step 1: Find stopped host and click delete
    const stoppedRow = await findHostRowByStatus(page, '已关机');
    expect(stoppedRow).not.toBeNull();
    const hostId = await stoppedRow.getAttribute('data-host-id');

    const deleteBtn = stoppedRow.locator('[data-testid="delete-button"]');
    await expect(deleteBtn).toBeEnabled();
    await deleteBtn.click();

    // Verify confirmation dialog appears
    const dialog = page.locator('[data-testid="confirm-dialog"]');
    await expect(dialog).toBeVisible();

    // Step 2: Cancel deletion
    await cancelDialog(page);
    await expect(dialog).not.toBeVisible();

    // Verify host still exists in list with status unchanged
    const rowAfterCancel = await findHostRowByStatus(page, '已关机');
    expect(rowAfterCancel).not.toBeNull();
    expect(await rowAfterCancel.getAttribute('data-host-id')).toBe(hostId);

    // Step 3: Re-click delete and confirm
    const deleteBtnAgain = rowAfterCancel.locator('[data-testid="delete-button"]');
    await deleteBtnAgain.click();
    await confirmDialogAndDelete(page);

    // Verify status changes to "删除中"
    const deletingRow = await findHostRowByStatus(page, '删除中');
    expect(deletingRow).not.toBeNull();
    expect(await deletingRow.getAttribute('data-host-id')).toBe(hostId);

    // Verify all action buttons are disabled during deletion
    const stopBtn = deletingRow.locator('[data-testid="stop-button"]');
    const startBtn = deletingRow.locator('[data-testid="start-button"]');
    const deleteBtnDuring = deletingRow.locator('[data-testid="delete-button"]');
    await expect(stopBtn).toBeDisabled();
    await expect(startBtn).toBeDisabled();
    await expect(deleteBtnDuring).toBeDisabled();

    // Step 4: Wait for row to disappear using expect.poll
    await waitForRowDisappearance(page, () => hostId);

    // Verify row is gone
    const rowAfterDelete = await findHostRowByStatus(page, '已关机');
    const rowWithId = rowAfterDelete ? await rowAfterDelete.getAttribute('data-host-id') : null;
    expect(rowWithId).not.toBe(hostId);

    // Step 5: Verify quota count decreased
    const finalQuota = await getQuotaCount(page);
    expect(finalQuota).toBe(initialQuota - 1);
  });

  // TC-052: Failed host deletion
  test('TC-052: 验证创建失败主机的删除', async ({ page }) => {
    await loginAndNavigate(page);

    // Record initial quota
    const initialQuota = await getQuotaCount(page);

    // Step 1: Find failed host and click delete
    const failedRow = await findHostRowByStatus(page, '创建失败');
    expect(failedRow).not.toBeNull();
    const hostId = await failedRow.getAttribute('data-host-id');

    const deleteBtn = failedRow.locator('[data-testid="delete-button"]');
    await expect(deleteBtn).toBeEnabled();
    await deleteBtn.click();

    // Verify confirmation dialog appears
    const dialog = page.locator('[data-testid="confirm-dialog"]');
    await expect(dialog).toBeVisible();

    // Step 2: Confirm deletion
    await confirmDialogAndDelete(page);

    // Verify status changes to "删除中"
    const deletingRow = await findHostRowByStatus(page, '删除中');
    expect(deletingRow).not.toBeNull();
    expect(await deletingRow.getAttribute('data-host-id')).toBe(hostId);

    // Verify all action buttons are disabled during deletion
    const stopBtn = deletingRow.locator('[data-testid="stop-button"]');
    const startBtn = deletingRow.locator('[data-testid="start-button"]');
    const deleteBtnDuring = deletingRow.locator('[data-testid="delete-button"]');
    await expect(stopBtn).toBeDisabled();
    await expect(startBtn).toBeDisabled();
    await expect(deleteBtnDuring).toBeDisabled();

    // Step 3: Wait for row to disappear using expect.poll
    await waitForRowDisappearance(page, () => hostId);

    // Verify row is gone
    const rowAfterDelete = await findHostRowByStatus(page, '创建失败');
    const rowWithId = rowAfterDelete ? await rowAfterDelete.getAttribute('data-host-id') : null;
    expect(rowWithId).not.toBe(hostId);

    // Step 4: Verify quota count decreased
    const finalQuota = await getQuotaCount(page);
    expect(finalQuota).toBe(initialQuota - 1);
  });
});
