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

- `explore --month` only accepts the next 6 months from today (SerpApi rejects outside that window with HTTP 400). `search.py` validates this client-side and fails fast. For farther-out dates, fall back to `search` with representative specific dates.

## Three subcommands

- `explore` → SerpApi `google_travel_explore`. Use for destination discovery (flexible origin and/or destination), area-based searches, month-based flexible dates, or flexible-date searches on a specific route (pass `--to`). Writes cache JSON only.
- `search` → SerpApi `google_flights`. Use for specific route + specific dates, one-way, round trip, or multi-city. Writes cache JSON only.
- `report` → consolidates one or more cache files into a single filterable HTML dashboard. Always the last call of a user turn.

## Picking the right command

| User request | Command |
|---|---|
| "Where can I fly from JFK cheap in July?" | `explore --from JFK --month 7` |
| "Cheap beach destinations from JFK, nonstop" | `explore --from JFK --interest beaches --stops nonstop` |
| "Compare GRU, LAX, JFK origins for Europe" | `explore --from GRU,LAX,JFK --area europe` |
| "GRU → LIS in July, nonstop" | `explore --from GRU --to LIS --month 7 --stops nonstop` |
| "JFK → LIS May 15-22, round trip" | `search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22` |
| "Cheapest JFK → LIS on May 15, sort by price, low emissions" | `search --from JFK --to LIS --depart 2026-05-15 --sort-by price --low-emissions` |
| "Morning departures only" | `search ... --outbound-times 6,12` |
| "JFK → LIS → MAD → JFK multi-city" | `search --multi-city-json '[...]'` |

## Cache and quota rules

The CLI stores each response in `~/.flight-search/<hash>.json` keyed by the full parameter set. SerpApi's free tier is 250 searches/month, so **respect the cache**.

- Reuse cache by default.
- Do not repeat an identical request unless the user explicitly asks for fresh data.
- Use `--no-cache` only for a forced refresh.
- Default TTL is 12 hours; override with `--cache-ttl <hours>`.
- Prefer one `explore` call over many `search` calls when the user is still deciding.

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
# Round trip
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22

# One way
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --oneway

# Cabin, stops, sort, low emissions
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22 --stops nonstop --class business --sort-by price --low-emissions

# Time-of-day windows (morning outbound 6-12h, evening return 18-23h)
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22 --outbound-times 6,12 --return-times 18,23

# Layover range, exclude hubs, deep search
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --layover 90,300 --exclude-conns LHR,CDG --deep-search

# Passengers (two adults, one child, one lap infant)
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22 --adults 2 --children 1 --infants-on-lap 1

# Multi-city
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search --multi-city-json '[{"departure_id":"JFK","arrival_id":"LIS","date":"2026-05-15"},{"departure_id":"LIS","arrival_id":"MAD","date":"2026-05-20"},{"departure_id":"MAD","arrival_id":"JFK","date":"2026-05-25"}]'
```

## Report examples

```bash
# Consolidate two explore runs into one dashboard
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" report \
  ~/.flight-search/abc123.json ~/.flight-search/def456.json

# Bare hashes also work
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" report abc123 def456

# Custom output path and title
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" report \
  --output ~/Desktop/july_flights.html --title "July flights shortlist" \
  ~/.flight-search/*.json
```

The report HTML ships with client-side filters for origin, destination, airline, stops, price range, and date range, plus sortable columns.

## Falling back to raw SerpApi

The CLI covers virtually every parameter of both engines. In the rare case it doesn't expose what you need, fetch the official SerpApi docs and use `curl` as a one-off — raw calls bypass the skill's cache.

- Explore engine: <https://serpapi.com/google-travel-explore-api>
- Flights engine: <https://serpapi.com/google-flights-api>
