---
name: flight-search
description: Search flights with Google Flights data via SerpApi. Handles destination discovery (flexible origin/destination, month-based flexible dates, area, interest, travel class), specific route searches (one-way, round trip, multi-city, time-of-day windows, layover ranges, airline include/exclude, sort by price/duration/emissions, low-emissions filter), and reuses a client-side cache to save SerpApi quota. Use when the assistant needs to find cheap flights, compare destinations, narrow by stops/duration/price/airline/class, filter by month or time of day, handle multi-city trips, or reuse cached searches.
---

# Flight Search

Search flights via `search.py`. Three subcommands:

- `explore` — flexible discovery / shortlist via `google_travel_explore` (writes cache JSON and terminal preview only).
- `search` — detail selected exact candidates via `google_flights` (writes cache JSON). Round trips require `--limit` unless the user explicitly approves uncapped detail.
- `report` — builds or updates a filterable HTML dashboard from detailed cache files. Use `--append --output <stable.html>` to keep updating the same dashboard for the same user query.

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
- Origin + destination + exact dates from a selected shortlist candidate → `search --limit 1` (or a small explicit limit)
- Multiple exact legs → `search --multi-city-json`
- After one or more detail searches → `report --append --output <stable_report.html> <detail_cache_files...>`

## Core rules

- Reuse cache by default. `--no-cache` only on explicit user request.
- Flexible requests (`from`, `to`, `after`, `before`, `month`, `4 or 5 days`, `cheap`, `compare destinations`, etc.) **must start with `explore`**. Do not expand flexible windows into a combinatorial grid of exact `search` calls.
- `explore` is not the final product. After every exploration, show the shortlist in chat and ask what the user wants to detail. Recommended options: detail the cheapest candidate, detail the 3 cheapest candidates, choose manually, or refine the exploration.
- Use `search` only to detail selected exact candidates from the shortlist. For round trips, `search` completes the SerpApi two-step flow: first outbound options, then return options via `departure_token`. Do not present outbound-only rows as full round trips.
- Round-trip detail must be capped with `--limit 1` or another small explicit value. The CLI refuses uncapped round-trip detail unless `--allow-uncapped-round-trip` is passed after explicit user approval.
- Before detailing selected candidates, tell the user the estimated number of new SerpApi requests. Cache hits cost 0.
- HTML is produced only after detail searches, not after exploration by default. For the same user query, always update the same HTML with `report --append --output <stable_report.html> <new_detail_cache...>`. Start a new HTML only for a new independent query/session or when the user explicitly asks.
- Always include the HTML path after running `report`. Never auto-open the browser — ask first.
- Follow the response flow in [references/output-format.md](references/output-format.md): explore shortlist → ask what to detail → detail selected candidates → append/update the HTML.
- Return Google Flights / Google Travel links with results.
- For structured user-facing questions: Claude Code `AskUserQuestion`; Codex Plan Mode `request_user_input`; Codex Default Mode → numbered-list fallback (see [references/setup.md](references/setup.md) §"Structured questions").

## References

- [references/checklist.md](references/checklist.md) — pre-use checks.
- [references/setup.md](references/setup.md) — setup, currency flow, preference changes.
- [references/usage.md](references/usage.md) — CLI patterns, intent → command table, examples.
- [references/output-format.md](references/output-format.md) — result presentation.

If the CLI cannot express something, fetch the SerpApi docs (<https://serpapi.com/google-flights-api>, <https://serpapi.com/google-travel-explore-api>) and use `curl` as a one-off fallback.
