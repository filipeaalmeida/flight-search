# Setup

Detailed procedures for the checks in [checklist.md](checklist.md). Load this file only when a check fails, or when the user asks to change a preference (see "Changing preferences later" at the bottom).

All procedures are idempotent.

## Structured questions

When this file says "ask the user with options", use your structured question tool.

- **Claude Code** → `AskUserQuestion` (always available).
- **Codex, Plan Mode** → `request_user_input` (supports options).
- **Codex, Default Mode** → no structured-question tool ships today. `ask_user_question` is an open RFC (openai/codex#9926). Fall back to a clean numbered list in chat and ask the user to reply with the option number:
  ```
  Pick one:
    1. Option A — description
    2. Option B — description
  ```

Do not simulate a UI in plain text when a real tool exists. Only fall back to the numbered-list pattern when no structured tool is available in the runtime.

## 1. Python venv

`setup.sh` creates a dedicated venv at `$SKILL_DIR/.venv/` and installs `requirements.txt` into it. It avoids PEP 668 "externally-managed-environment" errors on macOS and modern Linux distros.

```bash
bash "$SKILL_DIR/setup.sh"
```

All subsequent invocations of `search.py` **must** use this venv's interpreter:

```bash
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/search.py" <args>
```

## 2. SerpApi key

Drive this whenever the checklist's API-key check fails — at install time and at any later use.

`setup.sh` already creates `~/.flight-search/.env` with the placeholder `SERPAPI_API_KEY=PASTE_YOUR_KEY_HERE`. `search.py` also creates the same placeholder as a safety net on first run.

### Steps

1. **Verify first.** Re-read `~/.flight-search/.env`. If `SERPAPI_API_KEY` is already a real (non-empty, non-placeholder) key, skip this section.
2. **Ask via `AskUserQuestion` (Claude Code) or `ask_user_question` (Codex).** The tool must be invoked — do NOT ask this in prose.
   - **Header**: `SerpApi key`
   - **Body** (exact text, newlines preserved):
     ```
     A free SerpApi key is required (free tier: 250 searches/month).
     Get yours at https://serpapi.com/users/sign_up.
     ```
   - **Options** (pass each as a structured option with `label` and `description`):
     1. label: `I'll paste the key here`
        description: `Paste it in the next message; I'll write it to ~/.flight-search/.env`
     2. label: `I already pasted it in ~/.flight-search/.env`
        description: `I'll re-read the file to verify`
3. **Handle option 1** (`I'll paste the key here`):
   - Reply in prose: "Paste the key here:" and wait for the user's next message. That message body **is** the key.
   - Use your file-editing tools to replace `PASTE_YOUR_KEY_HERE` in `~/.flight-search/.env` with the pasted key.
   - Do not write the key elsewhere. Do not log or echo it back.
4. **Handle option 2** (`I already pasted it in ~/.flight-search/.env`):
   - Re-read `~/.flight-search/.env`. Verify `SERPAPI_API_KEY` is now a real key.
   - If still `PASTE_YOUR_KEY_HERE` or empty, tell the user the file was not updated and re-ask the question.
5. Confirm the skill is ready, then continue to §3 "Default currency".

## 3. Default currency

After the API key is set, ask the user what currency they want as default. This is a one-time question at install; re-runs of the checklist skip it when a valid `DEFAULT_CURRENCY` is already in `.env`.

### Check first

If `~/.flight-search/.env` already contains `DEFAULT_CURRENCY=<code>` with a non-empty 3-letter code, skip this section.

### Steps

1. **Ask via `AskUserQuestion` (Claude Code) or `ask_user_question` (Codex).** The tool must be invoked — do NOT ask this in prose.
   - **Header**: `Default currency`
   - **Body** (exact text):
     ```
     Which currency do you want as default?
     Saved in ~/.flight-search/.env; override per call with --currency.
     ```
   - **Options** (pass each as a structured option with `label` and `description`):
     1. label: `USD`
        description: `US Dollar`
     2. label: `EUR`
        description: `Euro`
     3. label: `BRL`
        description: `Brazilian Real`
     4. label: `GBP`
        description: `British Pound`
     5. label: `Other (I'll type it)`
        description: `Enter any 3-letter ISO code (JPY, MXN, CAD...)`
2. If the user picks `Other`, ask them to type the 3-letter ISO currency code (e.g., `JPY`, `MXN`, `CAD`).
3. Append `DEFAULT_CURRENCY=<CODE>` to `~/.flight-search/.env`. If the line already exists, replace it.
4. Tell the user the default is set, and that `--currency` on any CLI call still overrides it.

Why the assistant writes this too: the skill reads `DEFAULT_CURRENCY` from `.env` at runtime, but neither `setup.sh` nor `search.py` prompts for it — the file is the single source of truth.

## Changing preferences later

When the user asks to change a preference (e.g., "use EUR as default", "update my SerpApi key"), just edit `~/.flight-search/.env` directly.

- **Change default currency** → replace the `DEFAULT_CURRENCY=<old>` line with `DEFAULT_CURRENCY=<new>`. If the line is missing, add it.
- **Change API key** → replace the `SERPAPI_API_KEY=<old>` line with `SERPAPI_API_KEY=<new>`.

Confirm back to the user. No need to re-run `setup.sh` — only the `.env` changed.

## Why the assistant writes secrets (not the CLI)

`search.py` intentionally does **not** accept the API key via CLI argument. The real key is only written by the assistant's direct edit or by the user editing the file — keeping the flow transparent and auditable.
