# Pre-use Checklist

Run before every `search.py` invocation. Both checks are fast; do not skip them.

1. **Venv exists?** Check `$SKILL_DIR/.venv/bin/python`.
   - Missing → read [setup.md](setup.md) §"Python venv" and run the bootstrap.
2. **API key configured?** Check `~/.flight-search/.env` contains a line `SERPAPI_API_KEY=<value>` where `<value>` is non-empty and not `PASTE_YOUR_KEY_HERE`.
   - Missing or placeholder → read [setup.md](setup.md) §"SerpApi key" and drive the setup flow.

When both pass, invoke the CLI with the venv interpreter:

```bash
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" <args>
```

## Install-time extras

At install time only (not on every use), after the API key is configured, also run [setup.md](setup.md) §"Default currency" to ask the user for their preferred currency and persist it to `.env`. This is skipped on subsequent runs when `DEFAULT_CURRENCY` is already set.

## Preference changes

If the user later asks to change the API key or default currency, follow [setup.md](setup.md) §"Changing preferences later" — just edit `~/.flight-search/.env` directly.
