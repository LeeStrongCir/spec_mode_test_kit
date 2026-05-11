import { test, expect } from './fixtures/lecs-hosts-fixtures';

test.describe('SC-02: List Operation Matrix', () => {
  test('TC-010: List page renders paginated data table with required columns and create button', async ({ populatedListPage: page }) => {
    const table = page.locator('[data-testid="host-list-table"]');
    await expect(table).toBeVisible();

    const columns = page.locator('[data-testid="table-header"] th, thead th');
    await expect(columns.first()).toBeVisible();

    const headerTexts = await columns.allTextContents();
    expect(headerTexts.some(t => t.includes('主机名') || t.includes('ID'))).toBe(true);
    expect(headerTexts.some(t => t.includes('计费'))).toBe(true);
    expect(headerTexts.some(t => t.includes('状态'))).toBe(true);
    expect(headerTexts.some(t => t.includes('IP') || t.includes('私有'))).toBe(true);
    expect(headerTexts.some(t => t.includes('操作'))).toBe(true);

    const createButton = page.locator('[data-testid="create-lecs-host-btn"]');
    await expect(createButton).toBeVisible();
    await expect(createButton).toBeEnabled();

    const firstRow = page.locator('[data-testid="host-row"]').first();
    await expect(firstRow).toBeVisible();

    await expect(firstRow.locator('[data-testid="btn-stop"]')).toBeVisible();
    await expect(firstRow.locator('[data-testid="btn-start"]')).toBeVisible();
    await expect(firstRow.locator('[data-testid="btn-delete"]')).toBeVisible();
  });

  test('TC-011: Status labels render with correct colors per status', async ({ populatedListPage: page }) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      normal: { color: 'green', text: '正常' },
      stopped: { color: 'gray', text: '已关机' },
      creating: { color: 'blue', text: '创建中' },
      failed: { color: 'red', text: '创建失败' },
      deleting: { color: 'yellow', text: '删除中' },
    };

    for (const [status, { color, text }] of Object.entries(statusMap)) {
      const statusLabel = page.locator(`[data-testid="status-${status}"]`);
      const count = await statusLabel.count();
      if (count === 0) {
        continue;
      }

      const firstLabel = statusLabel.first();
      await expect(firstLabel).toBeVisible();
      await expect(firstLabel).toContainText(text);

      const classAttribute = await firstLabel.getAttribute('class');
      const styleAttribute = await firstLabel.getAttribute('style');
      const combined = `${classAttribute || ''} ${styleAttribute || ''}`.toLowerCase();

      const hasColorClass = combined.includes(color)
        || combined.includes(`bg-${color}`)
        || combined.includes(`text-${color}`)
        || combined.includes(`status-${color}`);

      expect(hasColorClass).toBe(true);
    }
  });

  test('TC-012: "Normal" state - stop enabled, start+delete disabled', async ({ populatedListPage: page }) => {
    const row = page.locator('[data-testid="status-normal"]').first();
    await expect(row).toBeVisible();

    const hostRow = row.locator('ancestor::tr').first();

    const stopBtn = hostRow.locator('[data-testid="btn-stop"]');
    const startBtn = hostRow.locator('[data-testid="btn-start"]');
    const deleteBtn = hostRow.locator('[data-testid="btn-delete"]');

    await expect(stopBtn).toBeEnabled();
    await expect(startBtn).toBeDisabled();
    await expect(deleteBtn).toBeDisabled();
  });

  test('TC-013: "Stopped" state - start+delete enabled, stop disabled', async ({ populatedListPage: page }) => {
    const row = page.locator('[data-testid="status-stopped"]').first();
    await expect(row).toBeVisible();

    const hostRow = row.locator('ancestor::tr').first();

    const stopBtn = hostRow.locator('[data-testid="btn-stop"]');
    const startBtn = hostRow.locator('[data-testid="btn-start"]');
    const deleteBtn = hostRow.locator('[data-testid="btn-delete"]');

    await expect(startBtn).toBeEnabled();
    await expect(deleteBtn).toBeEnabled();
    await expect(stopBtn).toBeDisabled();
  });

  test('TC-014: "Failed" state - only delete enabled, stop+start disabled', async ({ populatedListPage: page }) => {
    const row = page.locator('[data-testid="status-failed"]').first();
    await expect(row).toBeVisible();

    const hostRow = row.locator('ancestor::tr').first();

    const stopBtn = hostRow.locator('[data-testid="btn-stop"]');
    const startBtn = hostRow.locator('[data-testid="btn-start"]');
    const deleteBtn = hostRow.locator('[data-testid="btn-delete"]');

    await expect(deleteBtn).toBeEnabled();
    await expect(stopBtn).toBeDisabled();
    await expect(startBtn).toBeDisabled();
  });

  test('TC-015: "Deleting" state - all three buttons disabled', async ({ populatedListPage: page }) => {
    const row = page.locator('[data-testid="status-deleting"]').first();
    await expect(row).toBeVisible();

    const hostRow = row.locator('ancestor::tr').first();

    const stopBtn = hostRow.locator('[data-testid="btn-stop"]');
    const startBtn = hostRow.locator('[data-testid="btn-start"]');
    const deleteBtn = hostRow.locator('[data-testid="btn-delete"]');

    await expect(stopBtn).toBeDisabled();
    await expect(startBtn).toBeDisabled();
    await expect(deleteBtn).toBeDisabled();
  });
});
