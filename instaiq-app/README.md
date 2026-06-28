# InstaIQ — Instacart Customer Intelligence Platform (Frontend)

React + Vite + Tailwind frontend for the InstaIQ FastAPI backend, built during the AtliQ Technologies internship project.

## Setup

```bash
npm install
npm run dev
```

The app runs at `http://localhost:5173` and expects the FastAPI backend to be running at `http://localhost:8000` (see `src/lib/constants.js` to change the API base URL).

Make sure your FastAPI backend has CORS enabled for `http://localhost:5173`, e.g.:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Build

```bash
npm run build   # outputs to dist/
npm run preview # serve the production build locally
```

## Project structure

```
src/
  components/
    layout/      Sidebar, TopBar, PageShell, NavItem, StatusDot
    ui/           Card, Badge, Spinner, ErrorBanner, EmptyState, icons
    dashboard/    MetricCard, SegmentBarChart, ClvDonutChart, ChartTooltip
    explorer/     SegmentBadge, StatPill, ProgressBar, RecommendationsTable
    basket/       SimilarItemCard
    chat/         ChatBubble, ThinkingBubble, SuggestedQuestions
    report/       ChurnRiskTable
  pages/          One page component per route (Dashboard, UserExplorer, ...)
  hooks/          useHealth (health-check context, shared across pages)
  lib/            api.js (fetch client), constants.js, mockData.js
  App.jsx         Router + provider setup
  AppLayout.jsx   Sidebar + route definitions
  main.jsx        Vite entry point
```

## Notes on backend integration

- All API calls live in `src/lib/api.js`. If your response field names differ
  from what's assumed here (e.g. `/ask` returning something other than
  `{ answer: "..." }`), update `extractAnswer()` in that file.
- `src/lib/mockData.js` generates a deterministic mock breakdown of segment
  and CLV-tier counts from the total user count, since `/health` doesn't
  expose those directly. Swap in a real endpoint there once one exists.
- `src/lib/constants.js` holds the hardcoded summary stats (critical churn
  count, global reorder rate, avg CLV) and the static churn distribution
  table shown on the Weekly Report page — replace these with live data as
  those endpoints become available.
