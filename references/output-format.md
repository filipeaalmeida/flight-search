# Output Format

## Response flow

`explore` and `search` only write cache JSON (at `~/.flight-search/<hash>.json`). `explore` also prints a terminal shortlist. HTML is generated only after detail searches, using `report`.

For round-trip `search`, the cache must contain complete itineraries. The CLI first gets outbound options, then automatically calls SerpApi again with each selected `departure_token` to fetch compatible return flights. Do not preview or report outbound-only rows as if they were full round trips.

The CLI never opens the browser. The skill drives the UX via a shortlist → detail → report flow.

### Step 1 — Explore Shortlist, Then Ask What To Detail

Run `explore` first for flexible requests. Give a concise inline preview in chat (table or short list) from the structured results. Follow the column conventions under "Explore Output" below. 5–12 rows max.

Exploration is not the final product. Always ask what the user wants to detail next.

2. **Ask via the structured-question tool** — Claude Code `AskUserQuestion`, Codex Plan Mode `request_user_input`. In Codex Default Mode (no structured tool yet) fall back to a clean numbered list. See [setup.md](setup.md) §"Structured questions".
   - **Header**: `Detail`
   - **Body** (exact text):
     ```
     Which candidate(s) would you like to detail?
     ```
   - **Options** (pass each as a structured option with `label` and `description`):
     1. label: `Detail the cheapest`
        description: `Lowest-cost candidate; usually about 2 new requests if not cached`
     2. label: `Detail the top 3`
        description: `More comparison; usually about 6 new requests if not cached`
     3. label: `Choose manually`
        description: `Tell me the row number(s) or dates to detail`
     4. label: `Refine the search`
        description: `Adjust filters (dates, stops, airline, budget, destinations…)`
   - The tool's built-in "Chat about this" covers any other follow-up.

If the user picks `Refine the search`, gather the refinement in the next turn, re-run, then come back to Step 1 with the fresh preview.

### Step 2 — Detail Selected Candidates

Only runs after the user chooses one or more candidates to detail.

1. Run `search` for each selected exact candidate with a small explicit `--limit`:
   ```bash
   "$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" search \
     --from REC --to FLN --depart 2026-06-21 --return 2026-06-26 --limit 1
   ```
2. Before running, state the estimated new request count. Cache hits cost 0.
3. Use the `Data: <path>` lines from `search` as detail cache files for the report.

### Step 3 — Append/Update The HTML, Then Ask About Opening

Run this only after detail searches. For the same user query, always reuse the same output path with `--append`; this updates the sidecar manifest and regenerates the same HTML.

1. Run `report --append --output <stable_report.html>` with the new detail cache file(s):
   ```bash
   "$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" report \
     --append --output ~/.flight-search/output/rec_south_june_2026.html \
     ~/.flight-search/abc123.json
   ```
   Later detail requests for the same query use the same output path and only pass the newly detailed cache files. The manifest accumulates them.
2. Tell the user, in plain text: "HTML dashboard updated at `<path>`." — **always** include the path.
3. **Ask via the structured-question tool** — Claude Code `AskUserQuestion`, Codex Plan Mode `request_user_input`. In Codex Default Mode (no structured tool yet) fall back to a clean numbered list. See [setup.md](setup.md) §"Structured questions".
   - **Header**: `Open in browser?`
   - **Body** (exact text, substituting `<path>` with the real path):
     ```
     HTML dashboard:
     <path>

     Open it in your default browser now?
     ```
   - **Options** (pass as structured options, label only — no description needed):
     1. label: `Yes, open it`
     2. label: `No, just leave the path`
4. If `Yes, open it`, run the platform open command:
   - macOS: `open "<path>"`
   - Linux: `xdg-open "<path>"`
   - Windows: `start "" "<path>"`

**Important:** do not generate HTML after exploration by default. Do not create a new HTML for the same user query; append/update the existing output path. Start a new report only for a new independent query/session or when the user explicitly asks.

## Always include (in the inline preview)

- A Google Flights or Google Travel link for every result when available
- A short summary with total result count and price range
- The requested currency in every displayed price
- Clear indication of best or recommended options when the API provides them

## Explore output

Destination comparison table:

```text
| # | Origin | Destination | Country | Airport | Flight Price | Depart | Return | Days | Flight Duration | Airline | Stops | Link |
|---|--------|-------------|---------|---------|--------------|--------|--------|------|-----------------|---------|-------|------|
| 1 | JFK    | Lisbon      | Portugal | LIS    | $480         | 2026-07-10 | 2026-07-17 | 7 | 7h30 | TAP | 0 | Google |
```

HTML summary cards (in the dashboard, not the inline preview) highlight:

- Lowest price
- Highest price
- Destinations with price
- Destinations without price
- Number of origins

## Route search output

Flight options table:

```text
| # | Type | Origin | Destination | Price | Out Date | Out Time | Out Dur | Out Stops | Out Airline | Return Date | Return Time | Return Dur | Return Stops | Return Airline | Days | CO₂ | Link |
|---|------|--------|-------------|-------|----------|----------|---------|-----------|-------------|-------------|-------------|------------|--------------|----------------|------|-----|------|
| 1 | Best | JFK    | LIS         | $620  | 2026-05-15 | 21:30→09:00 | 7h30 | 0 | TAP | 2026-05-22 | 11:00→14:00 | 8h00 | 0 | TAP | 7 | 900kg | Google |
```

HTML summary cards highlight:

- Lowest price
- Highest price
- Total options
- Count of best-flight recommendations

## Presentation rules

- Sort priced explore results first by ascending price.
- Place explore results without price after priced results.
- Sort route search results by ascending price.
- Dim results without pricing instead of hiding them.
- Preserve stop counts and carbon data when the API provides them.
- For round trips, show outbound and return leg details in the same row; the displayed price is the complete itinerary price returned after the `departure_token` step.
