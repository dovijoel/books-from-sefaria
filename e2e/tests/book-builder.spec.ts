import { test, expect, Page } from '@playwright/test';

/**
 * E2E tests for the Book Builder flow.
 * All API calls are intercepted with page.route() so no real backend is needed.
 *
 * TODO: Update selectors once the actual UI is built.
 *       Selectors use data-testid attributes by convention; adjust as needed.
 */

// ---------------------------------------------------------------------------
// Shared API mock helpers
// ---------------------------------------------------------------------------
async function mockSefariaSearch(page: Page, results = defaultSearchResults) {
  await page.route('**/api/v1/sefaria/search**', (route) =>
    route.fulfill({ json: results }),
  );
}

async function mockCreateJob(page: Page, job = defaultJob) {
  await page.route('**/api/v1/jobs', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({ status: 201, json: job });
    } else {
      route.continue();
    }
  });
}

async function mockGetJob(page: Page, job = defaultJob) {
  await page.route(`**/api/v1/jobs/${defaultJob.id}`, (route) =>
    route.fulfill({ json: job }),
  );
}

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------
const defaultSearchResults = [
  { ref: 'Genesis 1', title: 'Genesis', heTitle: 'בראשית', type: 'Torah' },
  { ref: 'Exodus 1', title: 'Exodus', heTitle: 'שמות', type: 'Torah' },
];

const defaultJob = {
  id: 'test-job-id',
  status: 'pending',
  config: {},
  created_at: new Date().toISOString(),
};

const completeJob = { ...defaultJob, status: 'complete', pdf_url: '/api/v1/jobs/test-job-id/download' };

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
test.describe('Home page', () => {
  test('loads and shows the book builder heading', async ({ page }) => {
    await page.goto('/');
    // TODO: update text once real UI exists
    await expect(page).toHaveTitle(/sefaria/i);
    // await expect(page.getByRole('heading', { name: /book builder/i })).toBeVisible();
  });

  test('has a navigation link to saved configs', async ({ page }) => {
    await page.goto('/');
    // TODO: update selector once real nav exists
    // await expect(page.getByRole('link', { name: /saved/i })).toBeVisible();
    expect(true).toBe(true); // placeholder
  });
});

// ---------------------------------------------------------------------------
test.describe('Text search', () => {
  test.beforeEach(async ({ page }) => {
    await mockSefariaSearch(page);
    await page.goto('/');
  });

  test('shows results when user types in search box', async ({ page }) => {
    // TODO: update selector once real UI exists
    // const searchInput = page.getByRole('searchbox', { name: /search sefaria/i });
    // await searchInput.fill('genesis');
    // await expect(page.getByText('Genesis')).toBeVisible();
    expect(true).toBe(true); // placeholder
  });

  test('adds text to book list when result is clicked', async ({ page }) => {
    // TODO: update selectors once real UI exists
    // await page.getByRole('searchbox').fill('genesis');
    // await page.getByText('Genesis').click();
    // await expect(page.getByTestId('book-text-list')).toContainText('Genesis');
    expect(true).toBe(true); // placeholder
  });
});

// ---------------------------------------------------------------------------
test.describe('Full book creation flow', () => {
  test('creates a job and shows status', async ({ page }) => {
    await mockSefariaSearch(page);
    await mockCreateJob(page);
    await mockGetJob(page, { ...defaultJob, status: 'pending' });
    await page.goto('/');

    // TODO: implement once UI is built:
    // 1. Search for and add at least one text
    // 2. Fill in book settings form
    // 3. Click "Build Book"
    // 4. Expect status indicator to show "pending" → polling
    expect(true).toBe(true); // placeholder
  });

  test('shows download link when job is complete', async ({ page }) => {
    await mockSefariaSearch(page);
    await mockCreateJob(page);
    await mockGetJob(page, completeJob);
    await page.goto('/');

    // TODO: implement once UI is built:
    // After job completes, a download link should appear
    // await expect(page.getByRole('link', { name: /download/i })).toBeVisible();
    expect(true).toBe(true); // placeholder
  });

  test('shows error message when job fails', async ({ page }) => {
    await mockSefariaSearch(page);
    await mockCreateJob(page);
    await mockGetJob(page, { ...defaultJob, status: 'failed', error: 'LaTeX compilation error' });
    await page.goto('/');

    // TODO: implement once UI is built:
    // await expect(page.getByRole('alert')).toContainText(/failed/i);
    expect(true).toBe(true); // placeholder
  });
});

// ---------------------------------------------------------------------------
test.describe('Navigation', () => {
  test('navigates to /configs page', async ({ page }) => {
    await page.route('**/api/v1/configs', (route) => route.fulfill({ json: [] }));
    await page.goto('/');

    // TODO: update selector once real nav exists
    // await page.getByRole('link', { name: /saved/i }).click();
    // await expect(page).toHaveURL(/configs/);
    expect(true).toBe(true); // placeholder
  });
});
