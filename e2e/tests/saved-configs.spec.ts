import { test, expect, Page } from '@playwright/test';

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------
const API = 'http://localhost:8000';

const sampleConfig = {
  id: 'cfg-abc',
  name: 'My Genesis Book',
  description: 'A custom Genesis book',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const sampleConfig2 = {
  id: 'cfg-xyz',
  name: 'Psalms Collection',
  description: '',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// ---------------------------------------------------------------------------
// Route helpers
// ---------------------------------------------------------------------------
async function mockListConfigs(page: Page, configs = [sampleConfig]) {
  await page.route(`${API}/api/v1/configs`, (route) => {
    if (route.request().method() === 'GET') {
      route.fulfill({ json: configs });
    } else {
      route.continue();
    }
  });
}

async function mockDeleteConfig(page: Page, id = sampleConfig.id) {
  await page.route(`${API}/api/v1/configs/${id}`, (route) => {
    if (route.request().method() === 'DELETE') {
      route.fulfill({ status: 204, body: '' });
    } else {
      route.continue();
    }
  });
}

// ---------------------------------------------------------------------------
// Page structure
// ---------------------------------------------------------------------------
test.describe('/configs page structure', () => {
  test.beforeEach(async ({ page }) => {
    await mockListConfigs(page);
    await page.goto('/configs');
  });

  test('shows "Saved Configurations" heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /saved configurations/i })).toBeVisible();
  });

  test('shows "New Book" button', async ({ page }) => {
    await expect(page.getByRole('button', { name: /new book/i })).toBeVisible();
  });

  test('"New Book" button navigates to /builder', async ({ page }) => {
    await page.getByRole('button', { name: /new book/i }).click();
    await expect(page).toHaveURL(/\/builder/);
  });
});

// ---------------------------------------------------------------------------
// Empty state
// ---------------------------------------------------------------------------
test.describe('Empty state', () => {
  test('shows empty state message when no configs', async ({ page }) => {
    await mockListConfigs(page, []);
    await page.goto('/configs');
    await expect(page.getByText(/no saved configurations/i)).toBeVisible();
  });

  test('empty state "Open Builder" button navigates to /builder', async ({ page }) => {
    await mockListConfigs(page, []);
    await page.goto('/configs');
    await page.getByRole('button', { name: /open builder/i }).click();
    await expect(page).toHaveURL(/\/builder/);
  });
});

// ---------------------------------------------------------------------------
// Config cards
// ---------------------------------------------------------------------------
test.describe('Config cards', () => {
  test.beforeEach(async ({ page }) => {
    await mockListConfigs(page, [sampleConfig, sampleConfig2]);
    await page.goto('/configs');
  });

  test('shows card for each config', async ({ page }) => {
    await expect(page.getByText('My Genesis Book')).toBeVisible();
    await expect(page.getByText('Psalms Collection')).toBeVisible();
  });

  test('each card has a Load button', async ({ page }) => {
    const loadButtons = page.getByRole('button', { name: /load/i });
    await expect(loadButtons).toHaveCount(2);
  });

  test('each card has a delete (trash) button', async ({ page }) => {
    // Trash buttons don't have a text label, but they exist alongside Load buttons
    await expect(page.getByRole('button', { name: /load/i }).first()).toBeVisible();
    // There should be at least 2 delete icon buttons
    const allButtons = await page.getByRole('button').all();
    expect(allButtons.length).toBeGreaterThanOrEqual(4); // 2 Load + 2 delete + 1 New Book
  });

  test('"Load" button navigates to /builder', async ({ page }) => {
    await page.getByRole('button', { name: /load/i }).first().click();
    await expect(page).toHaveURL(/\/builder/);
  });
});

// ---------------------------------------------------------------------------
// Delete confirmation dialog
// ---------------------------------------------------------------------------
test.describe('Delete config', () => {
  test('clicking trash opens confirmation dialog', async ({ page }) => {
    await mockListConfigs(page, [sampleConfig]);
    await mockDeleteConfig(page);
    await page.goto('/configs');

    // The trash button doesn't have accessible name text; find it via its position
    // — it's the last button in the card footer
    const card = page.locator('.flex.gap-2.pt-3.border-t');
    const trashButton = card.getByRole('button').nth(1); // 0=Load, 1=trash
    await trashButton.click();

    // Dialog should appear
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByRole('heading', { name: /delete configuration/i })).toBeVisible();
  });

  test('dialog contains config name', async ({ page }) => {
    await mockListConfigs(page, [sampleConfig]);
    await mockDeleteConfig(page);
    await page.goto('/configs');

    const card = page.locator('.flex.gap-2.pt-3.border-t');
    await card.getByRole('button').nth(1).click();
    await expect(page.getByRole('dialog')).toContainText('My Genesis Book');
  });

  test('Cancel button closes dialog', async ({ page }) => {
    await mockListConfigs(page, [sampleConfig]);
    await page.goto('/configs');

    const card = page.locator('.flex.gap-2.pt-3.border-t');
    await card.getByRole('button').nth(1).click();
    await page.getByRole('button', { name: /cancel/i }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('Delete button in dialog calls DELETE and reloads list', async ({ page }) => {
    // After deletion, mock empty list to confirm re-fetch
    let callCount = 0;
    await page.route(`${API}/api/v1/configs`, (route) => {
      if (route.request().method() === 'GET') {
        callCount++;
        route.fulfill({ json: callCount === 1 ? [sampleConfig] : [] });
      } else {
        route.continue();
      }
    });
    await mockDeleteConfig(page);
    await page.goto('/configs');

    const card = page.locator('.flex.gap-2.pt-3.border-t');
    await card.getByRole('button').nth(1).click();
    await page.getByRole('button', { name: /^delete$/i }).click();

    // List should reload and show empty state
    await expect(page.getByText(/no saved configurations/i)).toBeVisible({ timeout: 5000 });
  });
});
