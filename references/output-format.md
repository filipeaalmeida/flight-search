# Output Format

## Response flow

`explore` and `search` only write cache JSON (at `~/.flight-search/<hash>.json`). They do **not** write HTML per call. A single consolidated HTML dashboard is produced by `report` at the end of the user's request, combining any number of cache files.

The CLI never opens the browser. The skill drives the UX via a two-step AskUserQuestion (Claude Code) / `ask_user_question` (Codex) flow:

### Step 1 — Preview inline, then ask

1. Give a concise inline preview in chat (table or short list) from the structured results. Follow the column conventions under "Explore Output" / "Route Search Output" below. 5–12 rows max.
2. **Ask via the structured-question tool** — Claude Code `AskUserQuestion`, Codex Plan Mode `request_user_input`. In Codex Default Mode (no structured tool yet) fall back to a clean numbered list. See [setup.md](setup.md) §"Structured questions".
   - **Header**: `Next`
   - **Body** (exact text):
     ```
     What would you like to do next?
     ```
   - **Options** (pass each as a structured option with `label` and `description`):
     1. label: `Show the HTML dashboard`
        description: `Full table, summary cards, Google Flights links`
     2. label: `Refine the search`
        description: `Adjust filters (dates, stops, airline, budget, destinations…)`
   - The tool's built-in "Chat about this" covers any other follow-up.

If the user picks `Refine the search`, gather the refinement in the next turn, re-run, then come back to Step 1 with the fresh preview.

### Step 2 — Generate consolidated HTML, then ask about opening

Only runs if the user picked `Show the HTML dashboard` in Step 1.

1. Run the `report` subcommand with **all** cache files involved in this request (the `Data: <path>` lines printed by each `explore` / `search` call). Example:
   ```bash
   "$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" report \
     ~/.flight-search/abc123.json ~/.flight-search/def456.json
   ```
   The report consolidates every row into a single filterable HTML with client-side filters for origin, destination, airline, stops, price range, and date range. It prints the output path as `Report: <path>`.
2. Tell the user, in plain text: "HTML dashboard generated at `<path>`." — **always** include the path.
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

**Important:** never call `report` more than once per user turn. Never write per-call HTML. One search request = one consolidated HTML.

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
| # | Type | Origin | Destination | Price | Total Duration | Stops | Airlines | Departure | Arrival | CO₂ | Link |
|---|------|--------|-------------|-------|----------------|-------|----------|-----------|---------|-----|------|
| 1 | Best | JFK    | LIS         | $620  | 7h30           | 0     | TAP      | 21:30     | 09:00   | 450kg | Google |
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
