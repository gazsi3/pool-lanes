# Pool Lanes — Swimming Finals Lane Analysis

Does lane 4 really win most? This project visualizes how lane assignment predicts race outcomes across all major swimming finals (Olympics, World Championships LCM/SCM, European Championships) from 2000 to 2024.

**Live site:** `https://<your-github-username>.github.io/pool-lanes/`

---

## What it shows

1. **Win & Top-3 Rate by Lane** — which lanes actually win most vs. the 12.5% baseline
2. **Performance vs. Expectation** — average position gain/loss relative to seed (e.g., a lane-3 swimmer finishing 2nd gained 1 position)
3. **Filterable Finals Database** — all finals with expandable lane-by-lane breakdowns

---

## Docker quickstart

```bash
# Start the frontend dev server (hot-reload on http://localhost:5173/pool-lanes/)
make dev

# Build the production site into dist/ (inside Docker — no local Node needed)
make build

# Build + serve the production bundle locally on http://localhost:8080/pool-lanes/
make preview

# Test scraper against one competition before a full run
make scrape-test

# Full scrape — all competitions 2000-2024 (takes hours, run overnight)
make scrape

# Push to GitHub → Actions builds and deploys to GitHub Pages automatically
make deploy
```

Run `make help` for all targets.

---

## Setup

### 1. GitHub repository

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/<you>/pool-lanes.git
git push -u origin main
```

Then in the GitHub repo settings → Pages → Source → **GitHub Actions**. The deploy workflow triggers automatically on every push to `main`.

### 2. Update the base URL

If your repository name differs from `pool-lanes`, change this line in [vite.config.ts](vite.config.ts):

```ts
base: "/your-repo-name/",
```

### 3. Frontend development

```bash
npm install
npm run dev      # http://localhost:5173/pool-lanes/
npm run build    # production build to dist/
```

---

## Scraper setup

The scraper uses Playwright (headless Chromium) to bypass Cloudflare on swimrankings.net.

### Install

```bash
pip install -r scraper/requirements.txt
playwright install chromium
```

### Test with a single year first

```bash
python -m scraper.main --competition "World Championships" --year 2022
```

This writes `public/data/finals.json` and `meta.json`. Check the output before running the full scrape.

### Full scrape (takes hours — run overnight)

```bash
python -m scraper.main
```

### Automated refresh

The GitHub Actions [scrape workflow](.github/workflows/scrape.yml) runs on the 1st of every month and can also be triggered manually from the Actions tab.

> **Note:** On the first run, verify that `scraper/config.py` `meet_type` values match what swimrankings.net uses for each competition. These values may need manual adjustment after inspecting the meet list URLs in a browser.

---

## Data model

Each record in `finals.json`:

```json
{
  "competition": "World Championships",
  "year": 2022,
  "location": "Budapest",
  "pool": "LCM",
  "event": "100m Freestyle",
  "gender": "M",
  "is_relay": false,
  "entries": [
    { "lane": 4, "name": "Dressel C.", "nationality": "USA",
      "final_time": "47.23", "position": 1, "dsq": false, "dns": false, "dnf": false }
  ]
}
```

Lane seeding logic:
- **8-lane pool:** 4 → 1st seed, 5 → 2nd, 3 → 3rd, 6 → 4th, 2 → 5th, 7 → 6th, 1 → 7th, 8 → 8th  
- **10-lane pool:** centre out, same principle

---

## Stack

| Layer | Technology |
|---|---|
| Scraper | Python 3.12, Playwright, BeautifulSoup |
| Frontend | React 18, TypeScript, Vite 5 |
| Charts | Recharts 2 |
| Table | TanStack Table v8 |
| Hosting | GitHub Pages |
| CI/CD | GitHub Actions |
