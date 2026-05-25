---
description: 'JavaScript and React conventions for the frontend'
applyTo: '**/*.{js,jsx,ts,tsx}'
excludeAgent: []
---
# JavaScript / React Instructions

Project-specific guidance for the Medicare Advantage Index frontend. The frontend is written in **JavaScript with JSX** (not TypeScript).

## Version and Runtime

- **Language**: JavaScript (JSX) — no TypeScript
- **Node version**: 20 LTS
- **Package manager**: npm
- **Framework**: React 18
- **Build tool**: Vite 5

## Tooling

| Tool | Command | Purpose |
|------|---------|---------|
| Dev server | `npm run dev` (from `frontend/`) | Start on port 5173 with HMR |
| Build | `npm run build` | Production build to `dist/` |
| Deploy | `npm run deploy` | Copy data, build, push to `gh-pages` branch |

No linter or formatter is currently configured. When adding one, prefer `eslint` + `prettier`.

## Project Structure

```text
frontend/
├── index.html
├── vite.config.js         # Sets base path to /kelly-taylor-test/ for production
├── public/
│   └── companies.json     # Generated data — gitignored, produced by data_fetcher.py
└── src/
    ├── main.jsx           # React entry point
    ├── App.jsx            # Root component: all state, filtering, sorting logic
    ├── App.css            # All styles — single flat stylesheet, no CSS modules
    └── components/
        └── CompanyDetail.jsx  # Slide-in detail panel for a single organization
```

## Team Conventions

### Preferred Patterns

- Use functional components with hooks — no class components
- Keep all search/filter/sort state in `App.jsx`; pass data down as props
- Use `useMemo` for derived lists (filtering + sorting); use `useRef` + `setTimeout` for debounce
- Fetch data once on mount from `${import.meta.env.BASE_URL}companies.json` — no API calls in production
- Use named exports for components (`export default function Foo`)

### Patterns to Avoid

- Do not add a routing library (React Router, etc.) — the app is a single view
- Do not use `dangerouslySetInnerHTML`
- Do not introduce a state management library (Redux, Zustand, etc.) — component state is sufficient
- Do not import from `node_modules` CSS; write styles in `App.css`

## Data Loading

All company data comes from a static `companies.json` file in `public/`. The fetch uses `import.meta.env.BASE_URL` so it works correctly both on `localhost:5173` (dev) and `kellytaylor-adhoc.github.io/kelly-taylor-test/` (production).

If adding a new field to the data, update `data_fetcher.py` to include it in the JSON output, then regenerate and copy the file.

## Styling

- All styles live in `App.css` — one flat file, no CSS modules or styled-components
- Use CSS custom properties for repeated values if the file grows
- Class naming is descriptive (`.modal-panel`, `.company-name`, `.tag-blue`) — no BEM or utility frameworks

## Import Organization

1. React and react-dom
2. Local components (`./components/...`)
3. Styles (`./App.css`)
