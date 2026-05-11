import { test, expect, Page, Locator } from '@playwright/test';

test.describe('SC-04: Lifecycle Control', () => {
  async function gotoHostList(page: Page) {
    await page.goto('/console/lecs-hosts/list');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('[data-testid="host-table"]')).toBeVisible();
  }

  async function loginAndNavigate(page: Page) {
    await page.goto('/login');
    await page.locator('[data-testid="username-input"]').fill('admin');
    await page.locator('[data-testid="password-input"]').fill('admin@123');
    await page.locator('[data-testid="login-button"]').click();
    await page.waitForURL('**/console**', { timeout: 5000 });
    await gotoHostList(page);
  }

  async function findHostRowByStatus(page: Page, statusText: string): Promise<Locator> {
    const row = page.locator(`[data-testid="host-row"]:has([data-testid="host-status"]:has-text("${statusText}"))`).first();
    await expect(row).toBeVisible();
    return row;
  }

  async function getHostStatus(row: Locator): Promise<string> {
    return row.locator('[data-testid="host-status"]').innerText();
  }

  function getBtnStop(row: Locator): Locator {
    return row.locator('[data-testid="host-btn-stop"]');
  }

  function getBtnStart(row: Locator): Locator {
    return row.locator('[data-testid="host-btn-start"]');
  }

  function getBtnDelete(row: Locator): Locator {
    return row.locator('[data-testid="host-btn-delete"]');
  }

  test('TC-040: 关机操作完整状态流转 - 正常 -> 关机中 -> 已关机', async ({ page }) => {
    await loginAndNavigate(page);

    const row = await findHostRowByStatus(page, '正常');

    await expect(getBtnStop(row)).toBeEnabled();
    await expect(getBtnStart(row)).toBeDisabled();
    await expect(getBtnDelete(row)).toBeDisabled();

    await getBtnStop(row).click();
    await expect(getBtnStop(row)).toBeDisabled();

    await expect.poll(async () => await getHostStatus(row)).toBe('关机中');

    await expect(getBtnStop(row)).toBeDisabled();
    await expect(getBtnStart(row)).toBeDisabled();
    await expect(getBtnDelete(row)).toBeDisabled();

    await expect.poll(async () => await getHostStatus(row), { timeout: 20000 }).toBe('已关机');

    await expect(getBtnStop(row)).toBeDisabled();
    await expect(getBtnStart(row)).toBeEnabled();

    await gotoHostList(page);
    const refreshedRow = await findHostRowByStatus(page, '已关机');
    await expect(refreshedRow).toBeVisible();
    await expect(getBtnStart(refreshedRow)).toBeEnabled();
    await expect(getBtnStop(refreshedRow)).toBeDisabled();
  });

  test('TC-041: 启动操作完整状态流转 - 已关机 -> 启动中 -> 正常', async ({ page }) => {
    await loginAndNavigate(page);

    const row = await findHostRowByStatus(page, '已关机');

    await expect(getBtnStart(row)).toBeEnabled();
    await expect(getBtnStop(row)).toBeDisabled();

    await getBtnStart(row).click();
    await expect(getBtnStart(row)).toBeDisabled();

    await expect.poll(async () => await getHostStatus(row)).toBe('启动中');

    await expect(getBtnStop(row)).toBeDisabled();
    await expect(getBtnStart(row)).toBeDisabled();
    await expect(getBtnDelete(row)).toBeDisabled();

    await expect.poll(async () => await getHostStatus(row), { timeout: 20000 }).toBe('正常');

    await expect(getBtnStop(row)).toBeEnabled();
    await expect(getBtnStart(row)).toBeDisabled();

    await gotoHostList(page);
    const refreshedRow = await findHostRowByStatus(page, '正常');
    await expect(refreshedRow).toBeVisible();
    await expect(getBtnStop(refreshedRow)).toBeEnabled();
    await expect(getBtnStart(refreshedRow)).toBeDisabled();
  });

  test('TC-042: 创建失败状态主机的启动 - 创建失败 -> 启动中 -> 正常', async ({ page }) => {
    await loginAndNavigate(page);

    const row = await findHostRowByStatus(page, '创建失败');

    await expect(getBtnStart(row)).toBeEnabled();
    await expect(getBtnStop(row)).toBeDisabled();

    await getBtnStart(row).click();
    await expect(getBtnStart(row)).toBeDisabled();

    await expect.poll(async () => await getHostStatus(row)).toBe('启动中');

    await expect(getBtnStop(row)).toBeDisabled();
    await expect(getBtnStart(row)).toBeDisabled();
    await expect(getBtnDelete(row)).toBeDisabled();

    await expect.poll(async () => await getHostStatus(row), { timeout: 20000 }).toBe('正常');

    await expect(getBtnStop(row)).toBeEnabled();
    await expect(getBtnStart(row)).toBeDisabled();

    await gotoHostList(page);
    const refreshedRow = await findHostRowByStatus(page, '正常');
    await expect(refreshedRow).toBeVisible();
    await expect(getBtnStop(refreshedRow)).toBeEnabled();
    await expect(getBtnStart(refreshedRow)).toBeDisabled();
  });

  test('TC-043: 过渡态防重复操作 - 关机中/启动中状态下按钮全部禁用', async ({ page }) => {
    await loginAndNavigate(page);

    const row = await findHostRowByStatus(page, '正常');
    const stopBtn = getBtnStop(row);
    const startBtn = getBtnStart(row);
    const deleteBtn = getBtnDelete(row);

    await stopBtn.click();
    await expect.poll(async () => await getHostStatus(row)).toBe('关机中');

    await expect(stopBtn).toBeDisabled();
    await expect(startBtn).toBeDisabled();
    await expect(deleteBtn).toBeDisabled();

    await stopBtn.click({ force: true });
    await startBtn.click({ force: true });
    await deleteBtn.click({ force: true });

    await expect.poll(async () => await getHostStatus(row), { timeout: 2000 }).toBe('关机中');

    await expect.poll(async () => await getHostStatus(row), { timeout: 20000 }).toBe('已关机');

    await expect(startBtn).toBeEnabled();
    await expect(stopBtn).toBeDisabled();
  });
});
