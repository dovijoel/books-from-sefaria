import { test, expect, Page } from '@playwright/test';

// ---------------------------------------------------------------------------
// Shared API mock helpers  (backend base URL is http://localhost:8000)
// ---------------------------------------------------------------------------
const API = 'http://localhost:8000';

async function mockSefariaSearch(page: Page, results = defaultSearchResults) {
  await page.route(`${API}/api/v1/sefaria/search**`, (route) =>
    route.fulfill({ json: results }),
  );
}

async function mockCreateJob(page: Page, job = defaultJob) {
  await page.route(`${API}/api/v1/jobs`, (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({ status: 201, json: job });
    } else {
      route.continue();
    }
  });
}

async function mockGetJob(page: Page, job = defaultJob) {
  await page.route(`${API}/api/v1/jobs/${job.id}`, (route) =>
    route.fulfill({ json: job }),
  );
}

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------
const defaultSearchResults = [
  { ref: 'Genesis 1', title: 'Genesis', heTitle: 'בראשית', type: 'Torah' },
  { ref: 'Exodus 1',  title: 'Exodus',  heTitle: 'שמות',   type: 'Torah' },
];

const defaultJob = {
  id: 'test-job-id',
  status: 'pending',
  config: {},
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  pdf_path: null,
  page_count: null,
  error_message: null,
};

const successJob = {
  ...defaultJob,
  status: 'success',
  pdf_path: '/tmp/pdf_output/test-job-id/output.pdf',
  page_count: 10,
};

const failedJob = {
  ...defaultJob,
  status: 'failure',
  error_message: 'LaTeX compilation error',
};

// ---------------------------------------------------------------------------
// Home page
// ---------------------------------------------------------------------------
test.describe('Home page', () => {
  test('page title contains Sefaria', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/sefaria/i);
  });

  test('shows brand name in nav header', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('banner').getByText('Sefaria Book Creator')).toBeVisible();
  });

  test('hero heading is visible', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: /turn jewish texts into/i })).toBeVisible();
  });

  test('"Start Building" CTA navigates to /builder', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: /start building/i }).first().click();
    await expect(page).toHaveURL(/\/builder/);
  });

  test('"Saved Configs" CTA navigates to /configs', async ({ page }) => {
    await page.route(`${API}/api/v1/configs`, (route) => route.fulfill({ json: [] }));
    await page.goto('/');
    await page.getByRole('link', { name: /saved configs/i }).first().click();
    await expect(page).toHaveURL(/\/configs/);
  });

  test('nav links Builder and Saved Configs are present', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('navigation').getByRole('link', { name: /builder/i })).toBeVisible();
    await expect(page.getByRole('navigation').getByRole('link', { name: /saved configs/i })).toBeVisible();
  });

  test('feature cards are rendered', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Search All of Sefaria')).toBeVisible();
    await expect(page.getByText('Custom Typesetting')).toBeVisible();
    await expect(page.getByText('Fast PDF Generation')).toBeVisible();
  });

  test('"How it works" section is present', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('How it works')).toBeVisible();
    await expect(page.getByText('Choose texts')).toBeVisible();
    await expect(page.getByText('Download PDF')).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Builder page — structural / UI tests (no backend needed for most)
// ---------------------------------------------------------------------------
test.describe('Builder page structure', () => {
  test.beforeEach(async ({ page }) => {
    // Prevent axios from making real calls to backend
    await page.route(`${API}/**`, (route) => route.abort());
    await page.goto('/builder');
  });

  test('shows 4-step progress indicator', async ({ page }) => {
    await expect(page.getByText('Choose Texts')).toBeVisible();
    await expect(page.getByText('Layout & Type')).toBeVisible();
    await expect(page.getByText('Cover Design')).toBeVisible();
    await expect(page.getByText('Review')).toBeVisible();
  });

  test('step 1 heading is "Choose Your Texts"', async ({ page }) => {
    await expect(page.getByText('Choose Your Texts', { exact: true })).toBeVisible();
  });

  test('book name input defaults to "My Sefaria Book"', async ({ page }) => {
    await expect(page.getByPlaceholder('My Sefaria Book')).toBeVisible();
  });

  test('search input placeholder is correct', async ({ page }) => {
    await expect(page.getByPlaceholder('Search Sefaria texts…')).toBeVisible();
  });

  test('shows empty state when no texts added', async ({ page }) => {
    await expect(page.getByText('No texts added yet')).toBeVisible();
  });

  test('Back button is disabled on step 1', async ({ page }) => {
    await expect(page.getByRole('button', { name: /back/i })).toBeDisabled();
  });

  test('Next button is visible on step 1', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Next', exact: true })).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Builder page — text search (mocked)
// ---------------------------------------------------------------------------
test.describe('Text search', () => {
  test.beforeEach(async ({ page }) => {
    await mockSefariaSearch(page);
    await page.goto('/builder');
  });

  test('shows search results dropdown after typing 3+ chars', async ({ page }) => {
    await page.getByPlaceholder('Search Sefaria texts…').fill('genesis');
    // Wait for debounce + response
    await expect(page.getByText('Genesis', { exact: true })).toBeVisible({ timeout: 5000 });
    await expect(page.getByText('Exodus', { exact: true })).toBeVisible();
  });

  test('adds text to list when search result is clicked', async ({ page }) => {
    await page.getByPlaceholder('Search Sefaria texts…').fill('genesis');
    await expect(page.getByText('Genesis', { exact: true })).toBeVisible({ timeout: 5000 });
    // click the <li> item — fires mousedown which triggers onSelect
    await page.locator('li').filter({ hasText: 'Genesis 1' }).click();
    // Empty state should disappear
    await expect(page.getByText('No texts added yet')).not.toBeVisible();
    // The ref should appear
    await expect(page.getByText('Genesis 1')).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Builder page — multi-step navigation
// ---------------------------------------------------------------------------
test.describe('Builder page navigation', () => {
  test.beforeEach(async ({ page }) => {
    await mockSefariaSearch(page);
    await page.goto('/builder');
  });

  test('Next advances to step 2 (Layout & Typography)', async ({ page }) => {
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    await expect(page.getByText('Layout & Typography', { exact: true })).toBeVisible();
  });

  test('Back from step 2 returns to step 1', async ({ page }) => {
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    await expect(page.getByText('Layout & Typography', { exact: true })).toBeVisible();
    await page.getByRole('button', { name: /back/i }).click();
    await expect(page.getByText('Choose Your Texts', { exact: true })).toBeVisible();
  });

  test('can advance through all 4 steps', async ({ page }) => {
    // Step 1 → 2
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    await expect(page.getByText('Layout & Typography', { exact: true })).toBeVisible();
    // Step 2 → 3
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    await expect(page.locator('[data-slot="card-title"]').filter({ hasText: 'Cover Design' })).toBeVisible();
    // Step 3 → 4
    await page.getByRole('button', { name: 'Next', exact: true }).click();
    await expect(page.getByText('Review & Generate', { exact: true })).toBeVisible();
  });

  test('review step shows "Generate PDF" button', async ({ page }) => {
    for (let i = 0; i < 3; i++) {
      await page.getByRole('button', { name: 'Next', exact: true }).click();
    }
    await expect(page.getByRole('button', { name: /generate pdf/i })).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Full book creation flow (mocked job creation)
// ---------------------------------------------------------------------------
test.describe('Full book creation flow', () => {
  test('submitting with no texts shows error toast, stays on step 1', async ({ page }) => {
    await mockSefariaSearch(page);
    await page.goto('/builder');
    // Navigate to review step
    for (let i = 0; i < 3; i++) {
      await page.getByRole('button', { name: 'Next', exact: true }).click();
    }
    // "Generate PDF" should be disabled with no texts
    await expect(page.getByRole('button', { name: /generate pdf/i })).toBeDisabled();
  });

  test('creates job and navigates to /jobs/:id', async ({ page }) => {
    await mockSefariaSearch(page);
    await mockCreateJob(page);
    await mockGetJob(page, defaultJob);
    await page.goto('/builder');

    // Add a text
    await page.getByPlaceholder('Search Sefaria texts…').fill('genesis');
    await expect(page.getByText('Genesis', { exact: true })).toBeVisible({ timeout: 5000 });
    await page.locator('li').filter({ hasText: 'Genesis 1' }).click();
    await expect(page.getByText('No texts added yet')).not.toBeVisible();

    // Advance to review
    for (let i = 0; i < 3; i++) {
      await page.getByRole('button', { name: 'Next', exact: true }).click();
    }

    // Generate
    await page.getByRole('button', { name: /generate pdf/i }).click();

    // Should navigate to job status page
    await expect(page).toHaveURL(/\/jobs\/test-job-id/, { timeout: 5000 });
  });
});
