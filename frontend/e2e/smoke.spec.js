const { test, expect } = require('@playwright/test');
const path = require('path');

function trackConsoleErrors(page) {
  const errors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', (err) => errors.push(err.message));
  return errors;
}

test('upload sample data, walk all four views, no console errors', async ({ page }) => {
  const errors = trackConsoleErrors(page);

  await page.goto('/');
  await expect(page.getByText('Temporal Spanner Analyzer')).toBeVisible();

  await page.getByRole('button', { name: 'Örnek Veri ile Dene' }).click();
  await expect(page.getByRole('button', { name: /^Spanner \(/ })).toBeVisible({ timeout: 15_000 });

  // Spanner view: metrics + at least one rendered graph. "indirildi" only
  // appears in the Spanner view's own summary banner (RightSidebar's
  // "Tasarruf %" text is unrelated and may be hidden on narrow viewports).
  await expect(page.getByText(/indirildi/)).toBeVisible();

  // Trends view.
  await page.getByRole('button', { name: 'Trends' }).click();
  await expect(page.getByText('klik zamansalı')).toBeVisible({ timeout: 15_000 });

  // Compare view.
  await page.getByRole('button', { name: 'Karşılaştır' }).click();
  await expect(page.getByRole('button', { name: /^Karşılaştır \(/ })).toBeVisible();

  // Explore view: search a word known to be in the sample corpus.
  await page.getByRole('button', { name: 'Keşfet' }).click();
  await page.getByPlaceholder('örnek: yapay').fill('yapay');
  await page.getByRole('button', { name: 'Ara' }).click();
  await expect(page.getByText(/klik,/)).toBeVisible({ timeout: 15_000 });

  // KWIC/concordance: raw sentence text is threaded through raw_documents
  // (see corpus_parser.py) purely client-side -- clicking "Bağlamda gör"
  // must show at least one matching sentence fragment, no extra request.
  await page.getByRole('button', { name: 'Bağlamda gör' }).first().click();
  await expect(page.getByText(/^Bağlamda:/)).toBeVisible();
  await expect(page.getByText(/eşleşme\)/)).toBeVisible();

  expect(errors, `console/page errors:\n${errors.join('\n')}`).toEqual([]);
});

test('large-graph upload does not freeze the page (regression)', async ({ page }) => {
  // Regression test for the multi-minute cytoscape 'cose' layout freeze:
  // upload a file with a large-ish vocabulary and confirm the page stays
  // responsive well within a few seconds, not tens of seconds/minutes.
  const errors = trackConsoleErrors(page);
  await page.goto('/');

  const filePath = path.resolve(__dirname, 'fixtures', 'many_words.csv');
  await page.locator('input[type="file"]').setInputFiles(filePath);

  const t0 = Date.now();
  await expect(page.getByRole('button', { name: /^Spanner \(/ })).toBeVisible({ timeout: 15_000 });
  await page.waitForTimeout(500);
  await expect(page.locator('body')).toBeVisible({ timeout: 5_000 });
  // ~900 vertices: cose (the physics layout GraphViewer used before the
  // fix) extrapolates to 30s+ at this scale (benchmarked ~4s@500,
  // ~16s@1000 nodes) -- grid (the fallback above 300 nodes) finishes in
  // well under a second. 12s leaves headroom for CI variance while still
  // failing hard if the large-graph safety net regresses.
  expect(Date.now() - t0).toBeLessThan(12_000);

  expect(errors, `console/page errors:\n${errors.join('\n')}`).toEqual([]);
});
