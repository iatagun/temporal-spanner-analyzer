const { defineConfig } = require('@playwright/test');

// E2E smoke tests. These exist because the real bugs found in this app so
// far (a multi-minute UI freeze on large graphs, a middleware fix that
// silently emptied request bodies) were only caught by actually driving
// the app in a browser -- unit tests and code review missed both. Backend
// and frontend dev servers are started together here so `npx playwright
// test` is self-contained both locally and in CI.
module.exports = defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: 'http://127.0.0.1:3010',
    trace: 'retain-on-failure',
  },
  webServer: [
    {
      command: 'python -m uvicorn backend.main:app --host 127.0.0.1 --port 8123',
      url: 'http://127.0.0.1:8123/api/health',
      cwd: '..',
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
      stdout: 'pipe',
      env: { CORS_ORIGINS: 'http://127.0.0.1:3010,http://localhost:3010' },
    },
    {
      command: 'npm run dev -- -p 3010',
      url: 'http://127.0.0.1:3010',
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
      env: { NEXT_PUBLIC_API_URL: 'http://127.0.0.1:8123' },
      stdout: 'pipe',
    },
  ],
});
