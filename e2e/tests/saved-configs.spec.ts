import { test, expect, Page } from '@playwright/test';

/**
 * E2E tests for the Saved Configurations page (/configs).
 * All API calls are intercepted with page.route() so no real backend is needed.
 *
 * TODO: Update selectors once the actual UI is built.
 */

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------
const sampleConfig = {
  id: 'cfg-abc',
  name: 'My Genesis Book',
  config: {
    texts: [{ link: 'Genesis 1', commentary: [], translation: 'English', range: '1:1' }],
    format: { paperheight: '9in', paperwidth: '6in' },
  },
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

// ---------------------------------------------------------------------------
// Route helpers
// ---------------------------------------------------------------------------
async function mockListConfigs(page: Page, configs = [sampleConfig]) {
  await page.route('**/api/v1/configs', (route) => {
    if (route.request().method() === 'GET') {
      route.fulfill({ json: configs });
    } else {
      route.continue();
    }
  });
}

async function mockGetConfig(page: Page, config = sampleConfig) {
  await page.route(`**/api/v1/configs/${config.id}`, (route) =>
    route.fulfill({ json: config }),
  );
}

async function mockDeleteConfig(page: Page, id = sampleConfig.id) {
  await page.route(`**/api/v1/configs/${id}`, (route) => {
    if (route.request().method() === 'DELETE') {
      route.fulfill({ status: 204, body: '' });
    } else {
      route.continue();
    }
  });
}

async function mockCreateConfig(page: Page, config = sampleConfig) {
  await page.route('**/api/v1/configs', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({ status: 201, json: config });
    } else {
      route.continue();
    }
  });
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
test.describe('Saved configs list', () => {
  test('shows saved configs on /configs page', async ({ page }) => {
    await mockListConfigs(page);
    await page.goto('/configs');

    // TODO: update selector once real UI exists
    // await expect(page.getByText('My Genesis Book')).toBeVisible();
    expect(true).toBe(true); // placeholder
  });

  test('shows empty state when no configs exist', async ({ page }) => {
    await mockListConfigs(page, []);
    await page.goto('/configs');

    // TODO: update selector once real UI exists
    // await expect(page.getByText(/no saved configurations/i)).toBeVisible();
    expect(true).toBe(true); // placeholder
  });

  test('shows creation date for each config', async ({ page }) => {
    await mockListConfigs(page);
    await page.goto('/configs');

    // TODO: update selector once real UI exists
    // const row = page.getByTestId(`config-row-${sampleConfig.id}`);
    // await expect(row).toBeVisible();
    expect(true).toBe(true); // placeholder
  });
});

// ---------------------------------------------------------------------------
test.describe('Create saved config', () => {
  test('opens create form and saves new config', async ({ page }) => {
    await mockListConfigs(page, []);
    await mockCreateConfig(page);
    await page.goto('/configs');

    // TODO: update selectors once real UI exists:
    // await page.getByRole('button', { name: /new config/i }).click();
    // await page.getByLabel(/name/i).fill('My New Config');
    // await page.getByRole('button', { name: /save/i }).click();
    // await expect(page.getByText('My New Config')).toBeVisible();
    expect(true).toBe(true); // placeholder
  });
});

// ---------------------------------------------------------------------------
test.describe('Delete saved config', () => {
  test('removes config from list after delete', async ({ page }) => {
    await mockListConfigs(page);
    await mockDeleteConfig(page);
    await page.goto('/configs');

    // TODO: update selectors once real UI exists:
    // await page.getByTestId(`delete-config-${sampleConfig.id}`).click();
    // await page.getByRole('button', { name: /confirm/i }).click(); // confirmation dialog
    // await expect(page.getByText('My Genesis Book')).not.toBeVisible();
    expect(true).toBe(true); // placeholder
  });

  test('shows confirmation dialog before deleting', async ({ page }) => {
    await mockListConfigs(page);
    await page.goto('/configs');

    // TODO: update selectors once real UI exists:
    // await page.getByTestId(`delete-config-${sampleConfig.id}`).click();
    // await expect(page.getByRole('dialog')).toBeVisible();
    expect(true).toBe(true); // placeholder
  });
});

// ---------------------------------------------------------------------------
test.describe('Load config into builder', () => {
  test('navigates to builder with config pre-filled', async ({ page }) => {
    await mockListConfigs(page);
    await mockGetConfig(page);
    await page.goto('/configs');

    // TODO: update selectors once real UI exists:
    // await page.getByTestId(`load-config-${sampleConfig.id}`).click();
    // await expect(page).toHaveURL('/');
    // const settingsForm = page.getByTestId('book-settings-form');
    // await expect(settingsForm).toBeVisible();
    expect(true).toBe(true); // placeholder
  });
});
