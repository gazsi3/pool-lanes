.PHONY: dev build preview scrape scrape-test deploy help

# ── Dev ────────────────────────────────────────────────────────────────────
dev:                          ## Start frontend dev server (hot-reload on :5173)
	docker compose up frontend

dev-build:                    ## Rebuild the frontend image then start dev
	docker compose up frontend --build

# ── Build for GitHub Pages ─────────────────────────────────────────────────
build:                        ## Compile the site into dist/ (inside Docker)
	docker compose run --rm --no-deps frontend npm run build

preview:                      ## Build + serve the production bundle on :8080
	docker compose --profile preview up preview --build

# ── Scraper ────────────────────────────────────────────────────────────────
scrape:                       ## Full scrape — all competitions 2000-2024 (hours)
	docker compose --profile scraper run --rm scraper

scrape-test:                  ## Quick test: 2022 World Championships only
	docker compose --profile scraper run --rm scraper \
	  python -m scraper.main --competition "World Championships" --year 2022

scrape-dry:                   ## Dry run — discover meets but don't write output
	docker compose --profile scraper run --rm scraper \
	  python -m scraper.main --competition "World Championships" --year 2022 --dry-run

# ── Deploy ─────────────────────────────────────────────────────────────────
deploy:                       ## Push main branch → GitHub Actions builds + deploys
	git push origin main

help:                         ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
