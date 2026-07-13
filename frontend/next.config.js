/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next.js's dev server only trusts "localhost" as a dev origin by
  // default; 127.0.0.1 (used by the Playwright e2e config so it doesn't
  // collide with a developer's own `npm run dev` on localhost:3004) gets
  // its HMR/dev-bootstrap requests silently blocked without this, which
  // in turn breaks client-side hydration -- every button click on the
  // page looked "successful" to Playwright but had no effect at all,
  // since React's event handlers never attached.
  allowedDevOrigins: ['127.0.0.1', 'localhost'],
};

module.exports = nextConfig;
