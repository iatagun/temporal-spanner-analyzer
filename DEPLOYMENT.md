# Temporal Spanner Analyzer — Dağıtım ve Commit Geçmişi

## Canlı Adresler

| Servis | URL |
|--------|-----|
| Frontend | https://frontend-teal-iota-ee3dg8j6wx.vercel.app |
| Backend API | https://temporal-spanner-api.onrender.com |
| API Health | https://temporal-spanner-api.onrender.com/api/health |
| GitHub | https://github.com/iatagun/temporal-spanner-analyzer |

## Ortam Değişkenleri

### Vercel (Frontend)
```
NEXT_PUBLIC_API_URL = https://temporal-spanner-api.onrender.com
```

### Render (Backend)
```
CORS_ORIGINS = https://frontend-teal-iota-ee3dg8j6wx.vercel.app,http://localhost:3004
SPANNER_VERIFY = (kapalı)
```

### Local (.env.local — frontend)
```
NEXT_PUBLIC_API_URL = http://127.0.0.1:8000
PORT = 3004
```

### Local (.env — backend)
```
CORS_ORIGINS = http://localhost:3004,http://127.0.0.1:3004
```

## Commit Geçmişi (son → ilk)

```
9901e9a feat: scale controls (min clique size, max cliques) + advanced toggle
92ab5ed fix: support year-only and year-month date formats in parse_label
631f271 fix: word-cliques response matches frontend (cliques array + total_snapshots)
ca209b3 docs: update all documentation to reflect current state
87f6adc chore: remove accidental file
efde62e fix: proper Turkish characters across all frontend text and sample data
52f97b8 ux: full-width layout
a01ea03 feat: 3-column layout with theoretical left + usage/file-templates right sidebar
c749de3 fix: trend timeline matching - new timelines no longer killed immediately
2aa1030 fix: line chart guard relaxed, single-point cliques show dots
af965cb fix: timestamp detection (1e9 threshold), Explore empty state with sample button
8045a83 fix: verification shows 'Atlandi' when skipped, trends line chart + clique words restored
23df6e6 chore: remove accidentally committed files
15e71f8 fix: sample.conllu tabs + refined UI polish (clean but not bare)
6899806 refactor: remove synthetic tab, sample CoNLL-U, clean academic design
ed1d857 perf: BK prune+Tomita pivot, verify optional, edge sort+bisect, CoNLL-U/VRT support
9725ce5 chore: update CORS with actual Vercel URL
9fd1bd7 fix: add python-multipart dependency
764a936 fix: use python -m uvicorn for Render deploy
8a975db refactor: Tailwind CSS, modular components, CORS env, deployment configs
```

## Deploy Komutları

```bash
# Backend → Render (otomatik, git push ile)
git push origin main

# Frontend → Vercel
cd frontend
vercel --prod --yes

# Force deploy (önbelleksiz)
vercel --prod --yes --force

# Environment variable ekleme (Vercel)
vercel env add NEXT_PUBLIC_API_URL production

# Local backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Local frontend
cd frontend && npm run dev    # http://localhost:3004

# Test
python -m pytest tests/ -v    # 37 test
```

## Vercel Proje Bilgisi
- Team: ilker2
- Project: frontend
- Framework: Next.js
- Build Command: npm run build
- Output Directory: .next

## Render Proje Bilgisi
- Service: temporal-spanner-api
- Type: Web Service
- Runtime: Python 3
- Build: pip install -r backend/requirements.txt
- Start: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
- Plan: Free
- Region: Frankfurt

## Ölçek Testi Sonuçları

| Veri | Cümle | Düğüm | Kenar | Klik | Süre |
|------|-------|-------|-------|------|------|
| sample.conllu | 20 | 62 | 228 | 32 | anlık |
| olcek_test.conllu | 200 | 52 | 1.875 | 692 | 0.27s |
| tr_pud_tarihli.conllu | 1.000 | 4.831 | 146k | 249k | 172s |
| PUD + min=5, max=100 | 1.000 | 4.831 | 146k | 100 | 5.3s |

## Dosya Yapısı

```
temporal-spanner-analyzer/
├── backend/
│   ├── main.py              FastAPI + CORS (.env)
│   ├── models.py            Pydantic modelleri
│   ├── requirements.txt     fastapi, uvicorn, pydantic, python-dotenv, python-multipart
│   ├── .env                 CORS_ORIGINS
│   ├── routers/
│   │   ├── spanner.py       /api/spanner, /api/upload, /api/export
│   │   ├── trends.py        /api/trends
│   │   ├── compare.py       /api/compare
│   │   └── explore.py       /api/word-cliques, /api/check-clique
│   ├── services/
│   │   ├── graph_builder.py  CSV/JSON/CoNLL-U/VRT → PMI çizge
│   │   ├── graph_utils.py    Bron–Kerbosch (Tomita pivot + budama)
│   │   ├── spanner_service.py Pipeline (verify opsiyonel, max_cliques)
│   │   ├── trend_analyzer.py Zaman pencereli klik evrimi (bisect + Jaccard)
│   │   └── corpus_parser.py  CoNLL-U / VRT ayrıştırıcı
│   └── algorithm/            Baligács (2026) Lemma/Theorem
├── frontend/
│   ├── app/
│   │   ├── page.js           Ana SPA (state + orkestrasyon)
│   │   ├── layout.js         Root layout
│   │   ├── globals.css       Tailwind v4
│   │   ├── components/       12 bileşen
│   │   ├── lib/              api.js, utils.js
│   │   └── public/           sample.conllu, olcek_test.conllu
│   ├── .env.local            NEXT_PUBLIC_API_URL, PORT=3004
│   ├── vercel.json           Vercel deploy config
│   └── postcss.config.mjs    Tailwind PostCSS
├── spanner/                  Saf Python algoritma kütüphanesi
├── tests/                    37 test (pytest)
├── docs/                     Algoritma dokümanları
├── render.yaml               Render deploy config
├── docker-compose.yml
├── Dockerfile
├── README.md
├── CLAUDE.md
├── TEMPORAL-SPANNER-PLANI.md
├── TEKNIK-SARTNAME.md
└── DEPLOYMENT.md             ← bu dosya
```
