---
name: flight-search
description: Search flights with Google Flights data via SerpApi. Handles destination discovery (flexible origin/destination, month-based flexible dates, area, interest, travel class), specific route searches (one-way, round trip, multi-city, time-of-day windows, layover ranges, airline include/exclude, sort by price/duration/emissions, low-emissions filter), and reuses a client-side cache to save SerpApi quota. Use when the assistant needs to find cheap flights, compare destinations, narrow by stops/duration/price/airline/class, filter by month or time of day, handle multi-city trips, or reuse cached searches.
---

# Flight Search

Search flights via `search.py`. Three subcommands:

- `explore` — flexible discovery or flexible-date route (writes cache JSON only).
- `search` — specific route with exact dates or multi-city (writes cache JSON only). Round trips automatically fetch compatible return flights with `departure_token` and store complete itineraries.
- `report` — consolidates one or more cache files into a single filterable HTML dashboard.

`SKILL_DIR` is this skill's directory.

**Before every use**, run the two checks in [references/checklist.md](references/checklist.md). Load [references/setup.md](references/setup.md) only if a check fails.

Invoke with the venv interpreter:

```bash
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" <args>
```

For the authoritative flag list, use the CLI's own help (cheaper than loading docs):

```bash
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" [explore|search] --help
```

## Engine choice

- Origin only → `explore`
- Origin + destination, dates flexible → `explore --to ...`
- Origin + destination + exact dates → `search`
- Multiple legs → `search --multi-city-json`
- End of the user's turn → `report <cache_files_from_this_turn>` (one consolidated HTML)

## Core rules

- Reuse cache by default. `--no-cache` only on explicit user request.
- For round trips, `search` must complete the SerpApi two-step flow: first outbound options, then return options via `departure_token`. Do not present outbound-only rows as full round trips.
- One user request = **one** consolidated HTML via `report`. Never generate multiple HTMLs for the same turn. `explore` and `search` only write cache JSON.
- Always include the HTML path in your response. Never auto-open the browser — ask first.
- Follow the two-step response flow in [references/output-format.md](references/output-format.md): (1) inline preview + ask "HTML dashboard or refine?"; (2) if HTML, run `report`, show the path, ask "open in browser?".
- Return Google Flights / Google Travel links with results.
- For structured user-facing questions: Claude Code `AskUserQuestion`; Codex Plan Mode `request_user_input`; Codex Default Mode → numbered-list fallback (see [references/setup.md](references/setup.md) §"Structured questions").

## References

- [references/checklist.md](references/checklist.md) — pre-use checks.
- [references/setup.md](references/setup.md) — setup, currency flow, preference changes.
- [references/usage.md](references/usage.md) — CLI patterns, intent → command table, examples.
- [references/output-format.md](references/output-format.md) — result presentation.

If the CLI cannot express something, fetch the SerpApi docs (<https://serpapi.com/google-flights-api>, <https://serpapi.com/google-travel-explore-api>) and use `curl` as a one-off fallback.
