# Temporal Spanner Analyzer — Frontend

Next.js 16 + React 19 + Tailwind CSS v4 + Cytoscape.js + D3.js

## Başlangıç

```bash
npm install
npm run dev    # http://localhost:3004
```

Backend'in http://127.0.0.1:8000 adresinde çalıştığından emin olun.
`.env.local` dosyasında `NEXT_PUBLIC_API_URL` ayarlıdır.

## Build

```bash
npm run build
npm start
```

## Deploy

```bash
vercel --prod
```

`vercel.json` ve ortam değişkenleri (`NEXT_PUBLIC_API_URL`) projeye dahildir.
