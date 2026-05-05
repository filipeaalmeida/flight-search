# Usage

Setup (venv + SerpApi key) is covered in [setup.md](setup.md). Run that checklist before the first search of a session. The examples below assume the skill is ready.

The authoritative, always-current flag list lives in the CLI itself:

```bash
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" --help
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --help
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --help
```

Use `--help` when you just need to confirm a flag name or value — it's cheaper than loading this file.

## Known API limitations

- `explore --month` only accepts the next 6 months from today (SerpApi rejects outside that window with HTTP 400). `search.py` validates this client-side and fails fast. For farther-out dates, explain the limitation and ask before using representative exact dates.
- `explore --duration` supports SerpApi's coarse flexible values only: `weekend`, `1week`, `2weeks`. If the user asks for a custom duration like 4 or 5 days, use `explore` first for shortlist discovery, then ask which candidate(s) to detail exactly.

## Three subcommands

- `explore` → SerpApi `google_travel_explore`. Use for destination discovery (flexible origin and/or destination), area-based searches, month-based flexible dates, or flexible-date searches on a specific route (pass `--to`). Writes cache JSON and prints a terminal shortlist. This is the first step for flexible travel requests.
- `search` → SerpApi `google_flights`. Use only to detail selected exact candidates after exploration, or for genuinely exact one-way / multi-city requests. Writes cache JSON. For round trips, it follows SerpApi's `departure_token` flow and requires `--limit` unless the user explicitly approves uncapped detail.
- `report` → builds or updates a filterable HTML dashboard from detailed cache files. For the same user query, use `--append --output <stable_report.html>` so later detail searches update the same file.

## Picking the right command

| User request | Command |
|---|---|
| "Where can I fly from JFK cheap in July?" | `explore --from JFK --month 7` |
| "Cheap beach destinations from JFK, nonstop" | `explore --from JFK --interest beaches --stops nonstop` |
| "Compare GRU, LAX, JFK origins for Europe" | `explore --from GRU,LAX,JFK --area europe` |
| "GRU → LIS in July, nonstop" | `explore --from GRU --to LIS --month 7 --stops nonstop` |
| "JFK → LIS May 15-22, round trip" | `search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22 --limit 1` |
| "Cheapest JFK → LIS on May 15, sort by price, low emissions" | `search --from JFK --to LIS --depart 2026-05-15 --oneway --sort-by price --low-emissions` |
| "Morning departures only" | `search ... --outbound-times 6,12` |
| "JFK → LIS → MAD → JFK multi-city" | `search --multi-city-json '[...]'` |

Flexible windows such as "depart after 2026-06-21, return by 2026-06-30, 4 or 5 days" are **not** a license to enumerate every date pair with `search`. Run `explore` first, preview the shortlist, then ask what to detail.

## Cache and quota rules

The CLI stores each response in `~/.flight-search/<hash>.json` keyed by the full parameter set. SerpApi's free tier is 250 searches/month, so **respect the cache**.

- Reuse cache by default.
- Do not repeat an identical request unless the user explicitly asks for fresh data.
- Use `--no-cache` only for a forced refresh.
- Default TTL is 12 hours; override with `--cache-ttl <hours>`.
- Prefer one `explore` call over many `search` calls when the user is still deciding.
- Before detail searches, state the estimated number of new SerpApi requests. Cache hits cost 0.
- Round-trip `search` uses additional cached SerpApi calls: one `departure_token` call per outbound option being completed. `--limit <n>` caps how many outbound options are completed. Round-trip detail without `--limit` fails fast unless `--allow-uncapped-round-trip` is explicitly passed.

Inspect cached results manually:

```bash
ls -lt ~/.flight-search/
cat ~/.flight-search/<hash>.json | python -m json.tool
```

## Default currency

Set `DEFAULT_CURRENCY` in `~/.flight-search/.env` (e.g., `DEFAULT_CURRENCY=BRL`) to skip passing `--currency` every call. `--currency` still overrides when specified.

## Explore examples

```bash
# Cheapest destinations from one origin, anywhere
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from JFK

# Multiple origins
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from JFK,LAX,ORD

# Filter by month (1-12; 0 = any of next 6 months)
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from JFK --month 7

# Flexible-date search on a specific route (explore mode, returns flights for that route)
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from GRU --to LIS --month 7 --stops nonstop

# Stops + duration + max price
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from JFK --stops nonstop --duration weekend --max-price 600

# Area
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from JFK --area europe
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from LAX --area caribbean

# Interest (mutually exclusive with --travel-mode flight)
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from JFK --interest beaches

# Airlines
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from JFK --include-airlines STAR_ALLIANCE

# Localization
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" explore --from GRU --currency BRL --hl pt --gl br
```

## Search examples

```bash
# Round trip detail for one selected candidate
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22 --limit 1

# Round trip, completing only the cheapest outbound option to save quota
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from GRU --to MIA --depart 2026-05-28 --return 2026-06-03 --sort-by price --limit 1

# One way
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --oneway

# Cabin, stops, sort, low emissions
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22 --stops nonstop --class business --sort-by price --low-emissions --limit 1

# Time-of-day windows (morning outbound 6-12h, evening return 18-23h)
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22 --outbound-times 6,12 --return-times 18,23 --limit 1

# Layover range, exclude hubs, deep search
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --oneway --layover 90,300 --exclude-conns LHR,CDG --deep-search

# Passengers (two adults, one child, one lap infant)
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22 --adults 2 --children 1 --infants-on-lap 1 --limit 1

# Multi-city
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --multi-city-json '[{"departure_id":"JFK","arrival_id":"LIS","date":"2026-05-15"},{"departure_id":"LIS","arrival_id":"MAD","date":"2026-05-20"},{"departure_id":"MAD","arrival_id":"JFK","date":"2026-05-25"}]'
```

## Report examples

```bash
# Create/update the detail dashboard for a query
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" report \
  --append --output ~/.flight-search/output/rec_south_june_2026.html \
  ~/.flight-search/detail123.json

# Bare hashes also work
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" report \
  --append --output ~/.flight-search/output/rec_south_june_2026.html \
  detail456

# Custom output path and title for a new independent query
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" report \
  --append --output ~/Desktop/lisbon_detail.html --title "Lisbon detail" \
  ~/.flight-search/detail789.json
```

`report --append --output <path>` writes a sidecar manifest at `<path>.manifest.json`. Later calls with the same output path merge the new cache files into the manifest and regenerate the same HTML. Use plain `report` without `--append` only for ad hoc or explicitly independent dashboards.

## Falling back to raw SerpApi

The CLI covers virtually every parameter of both engines. In the rare case it doesn't expose what you need, fetch the official SerpApi docs and use `curl` as a one-off — raw calls bypass the skill's cache.

- Explore engine: <https://serpapi.com/google-travel-explore-api>
- Flights engine: <https://serpapi.com/google-flights-api>
