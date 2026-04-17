# flight-search

A skill that searches flights using Google Flights data via SerpApi. Works with both **Claude Code** and **Codex**.

The skill understands requests like:

- "Find cheap flights from JFK in July, beach destinations, nonstop"
- "GRU → LIS in July, nonstop, sort by price"
- "JFK → LIS May 15 to May 22, economy, morning departures only"
- "Multi-city JFK → LIS → MAD → JFK in May"
- "Compare Lisbon, Madrid and Paris from JFK in August"

It returns results with prices, stops, duration, CO₂, and links to Google Flights.

## Features

- **Both search modes** — flexible destination/date discovery (`google_travel_explore`) and specific route search (`google_flights`).
- **Full API coverage** — month-based flexibility, time-of-day windows, layover ranges, hubs to exclude, airline include/exclude, sort, low-emissions filter, multi-city, cabin class, passengers, bags. Run `search.py --help` for the full flag list.
- **Consolidated filterable HTML** — `search.py report <cache_files...>` merges any number of searches into a single dashboard with client-side filters (origin, destination, airline, stops, price range, date range) and sortable columns. `explore` / `search` only write cache JSON; the HTML is always built by one `report` call at the end.
- **Client-side cache** — each response is saved in `~/.flight-search/<hash>.json` keyed by the full parameter set. Identical queries reuse the cache instead of burning SerpApi quota (default TTL 12h, override with `--cache-ttl`, bypass with `--no-cache`). SerpApi's free tier is 250 searches/month — this matters.
- **Self-contained venv** — `setup.sh` creates `.venv/` inside the skill directory so the skill never touches system Python (PEP 668-safe on macOS and modern Linux).
- **Assistant-driven setup** — on first run the skill creates a placeholder `.env` and the agent walks the user through pasting the SerpApi key (or the user edits the file directly).

## Install

### Claude Code

Paste this into Claude Code and run it:

```
Install the flight-search skill from https://github.com/filipeaalmeida/flight-search
```

### Codex

Paste this into Codex and run it:

```
Install the flight-search skill from https://github.com/filipeaalmeida/flight-search
```

### Instructions for the installing agent (do not skip)

When the user asks to install this skill, execute **all** of the following. Do not stop after the clone+setup.sh step.

1. **Clone** the repo into the correct skills directory:
   - Claude Code: `~/.claude/skills/flight-search`
   - Codex: `~/.codex/skills/flight-search`
2. **Run** `bash <skill-dir>/setup.sh` to create the venv and install dependencies.
3. **Drive the SerpApi-key setup interactively.** Read `<skill-dir>/references/setup.md` §2 and use your structured-question tool — `AskUserQuestion` (Claude Code) or `ask_user_question` (Codex) — to present the three options (paste now / already edited / open signup page). Do not tell the user to paste the key into a file in prose; use the structured tool.
4. **Drive the default-currency setup.** Read `<skill-dir>/references/setup.md` §3 and ask the user (via the same structured-question tool) for their default currency. Write the choice to `~/.flight-search/.env`.
5. Only after steps 3 and 4 are complete, tell the user the skill is ready.

### Manual install

If you'd rather configure it yourself without an agent:

```bash
# Claude Code (user-level skill)
git clone https://github.com/filipeaalmeida/flight-search ~/.claude/skills/flight-search
bash ~/.claude/skills/flight-search/setup.sh

# or Codex
git clone https://github.com/filipeaalmeida/flight-search ~/.codex/skills/flight-search
bash ~/.codex/skills/flight-search/setup.sh

# then edit ~/.flight-search/.env:
#   SERPAPI_API_KEY=<your key>
#   DEFAULT_CURRENCY=USD     # optional; override per call with --currency
```

## SerpApi key

On first run the skill creates `~/.flight-search/.env` with a placeholder. Paste the key into chat (the agent writes it) or edit the file directly — either works.

Get a free key at https://serpapi.com/users/sign_up (250 searches/month on the free plan).

Optional: set `DEFAULT_CURRENCY=BRL` (or any ISO code) in the same `.env` to change the default currency without passing `--currency` every time.

## Using the CLI directly

```bash
SKILL_DIR=~/.claude/skills/flight-search
PY="$SKILL_DIR/.venv/bin/python"

# discover cheap destinations in July (writes cache JSON, prints path)
"$PY" "$SKILL_DIR/search.py" explore --from JFK --month 7

# specific route with flexible dates
"$PY" "$SKILL_DIR/search.py" explore --from GRU --to LIS --month 7 --stops nonstop

# specific route, specific dates, sort by price
"$PY" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22 --sort-by price

# consolidate everything above into one filterable HTML dashboard
"$PY" "$SKILL_DIR/search.py" report ~/.flight-search/*.json
```

`explore` and `search` only write cache JSON. A single HTML dashboard is built by `report` at the end, merging any number of cache files. The CLI never opens the browser — the agent asks the user first.

## How it works

- `SKILL.md` — orchestration the agent follows
- `search.py` — deterministic CLI that talks to SerpApi (caching, name→KGID mapping, response normalization)
- `setup.sh` — bootstraps `.venv/` and installs dependencies
- `references/` — reference docs loaded on demand (`checklist.md`, `setup.md`, `usage.md`, `output-format.md`)

## Disclaimer

This project is not affiliated with, endorsed by, or sponsored by Google or SerpApi. "Google Flights" is a trademark of Google LLC. Flight data is retrieved via SerpApi using the user's own API key.

## License

MIT — see [LICENSE](LICENSE).
