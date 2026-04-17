#!/usr/bin/env python3
"""Google Flights Search via SerpApi."""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

SERPAPI_URL = "https://serpapi.com/search.json"
CACHE_DIR = Path.home() / ".flight-search"
OUTPUT_DIR = CACHE_DIR / "output"
DEFAULT_CACHE_TTL_HOURS = 12

INTEREST_MAP = {
    "beaches": "/m/0b3yr",
    "outdoors": "/g/11bc58l13w",
    "museums": "/m/09cmq",
    "history": "/m/03g3w",
    "skiing": "/m/071k0",
}

STOPS_MAP = {
    "any": 0,
    "nonstop": 1,
    "1": 2,
    "2": 3,
}

DURATION_MAP = {
    "weekend": 1,
    "1week": 2,
    "2weeks": 3,
}

CLASS_MAP = {
    "economy": 1,
    "premium": 2,
    "business": 3,
    "first": 4,
}

TYPE_MAP = {
    "round-trip": 1,
    "oneway": 2,
    "one-way": 2,
    "multi-city": 3,
}

TRAVEL_MODE_MAP = {
    "all": 0,
    "flight": 1,
}

SORT_BY_MAP = {
    "top": 1,
    "price": 2,
    "departure": 3,
    "arrival": 4,
    "duration": 5,
    "emissions": 6,
}

AREA_MAP = {
    # Continents / regions
    "south-america": "/m/06n3y",
    "europe": "/m/02j9z",
    "north-america": "/m/059g4",
    "asia": "/m/0j0k",
    "africa": "/m/0dg3n1",
    "oceania": "/m/05nrg",
    "central-america": "/m/01tzh",
    "caribbean": "/m/0261m",
    "latin-america": "/m/04pnx",
    # Sub-regions
    "eastern-europe": "/m/09b69",
    "western-europe": "/m/0852h",
    "southern-europe": "/m/0250wj",
    "northern-europe": "/m/01531v",
    "southeast-asia": "/m/073q1",
    "east-asia": "/m/02qnk",
    "south-asia": "/m/06nn1",
    "middle-east": "/m/04wsz",
    # Americas
    "br": "/m/015fr", "brazil": "/m/015fr",
    "ar": "/m/0jgd", "argentina": "/m/0jgd",
    "cl": "/m/01p1v", "chile": "/m/01p1v",
    "co": "/m/01ls2", "colombia": "/m/01ls2",
    "pe": "/m/016wzw", "peru": "/m/016wzw",
    "uy": "/m/07twz", "uruguay": "/m/07twz",
    "py": "/m/05v10", "paraguay": "/m/05v10",
    "ec": "/m/02k1b", "ecuador": "/m/02k1b",
    "bo": "/m/0165v", "bolivia": "/m/0165v",
    "ve": "/m/07ylj", "venezuela": "/m/07ylj",
    "mx": "/m/0b90_r", "mexico": "/m/0b90_r",
    "us": "/m/09c7w0", "usa": "/m/09c7w0",
    "ca": "/m/0d060g", "canada": "/m/0d060g",
    "cu": "/m/0d04z6", "cuba": "/m/0d04z6",
    "do": "/m/027rn", "dominican-republic": "/m/027rn",
    "pa": "/m/05qx1", "panama": "/m/05qx1",
    # Europe
    "pt": "/m/05r4w", "portugal": "/m/05r4w",
    "es": "/m/06mkj", "spain": "/m/06mkj",
    "fr": "/m/0f8l9c", "france": "/m/0f8l9c",
    "it": "/m/03rjj", "italy": "/m/03rjj",
    "uk": "/m/07ssc", "united-kingdom": "/m/07ssc",
    "de": "/m/0345h", "germany": "/m/0345h",
    "nl": "/m/059j2", "netherlands": "/m/059j2",
    "gr": "/m/035qy", "greece": "/m/035qy",
    "tr": "/m/01znc_", "turkey": "/m/01znc_",
    "ch": "/m/06mzp", "switzerland": "/m/06mzp",
    "at": "/m/0h7x", "austria": "/m/0h7x",
    "cz": "/m/01mjq", "czech-republic": "/m/01mjq",
    "pl": "/m/05qhw", "poland": "/m/05qhw",
    "hu": "/m/03gj2", "hungary": "/m/03gj2",
    "be": "/m/0154j", "belgium": "/m/0154j",
    "ie": "/m/03rt9", "ireland": "/m/03rt9",
    "se": "/m/0d0vqn", "sweden": "/m/0d0vqn",
    "dk": "/m/0k6nt", "denmark": "/m/0k6nt",
    "no": "/m/05b4w", "norway": "/m/05b4w",
    "fi": "/m/02vzc", "finland": "/m/02vzc",
    "is": "/m/03rj0", "iceland": "/m/03rj0",
    "hr": "/m/01pj7", "croatia": "/m/01pj7",
    "ro": "/m/06c1y", "romania": "/m/06c1y",
    "bg": "/m/015qh", "bulgaria": "/m/015qh",
    "si": "/m/06t8v", "slovenia": "/m/06t8v",
    "sk": "/m/06npd", "slovakia": "/m/06npd",
    "ee": "/m/02kmm", "estonia": "/m/02kmm",
    "lv": "/m/04g5k", "latvia": "/m/04g5k",
    "lt": "/m/04gzd", "lithuania": "/m/04gzd",
    "mt": "/m/04v3q", "malta": "/m/04v3q",
    "cy": "/m/01ppq", "cyprus": "/m/01ppq",
    # Asia and Oceania
    "jp": "/m/03_3d", "japan": "/m/03_3d",
    "th": "/m/07f1x", "thailand": "/m/07f1x",
    "au": "/m/0chghy", "australia": "/m/0chghy",
    "nz": "/m/0ctw_b", "new-zealand": "/m/0ctw_b",
    "kr": "/m/06qd3", "south-korea": "/m/06qd3",
    "cn": "/m/0d05w3", "china": "/m/0d05w3",
    "in": "/m/03rk0", "india": "/m/03rk0",
    "id": "/m/03ryn", "indonesia": "/m/03ryn",
    "sg": "/m/06t2t", "singapore": "/m/06t2t",
    "vn": "/m/01crd5", "vietnam": "/m/01crd5",
    "ph": "/m/05v8c", "philippines": "/m/05v8c",
    "my": "/m/09pmkv", "malaysia": "/m/09pmkv",
    "kh": "/m/01xbgx", "cambodia": "/m/01xbgx",
    "tw": "/m/06f32", "taiwan": "/m/06f32",
    "lk": "/m/06m_5", "sri-lanka": "/m/06m_5",
    "np": "/m/016zwt", "nepal": "/m/016zwt",
    "mn": "/m/04w8f", "mongolia": "/m/04w8f",
    # Middle East and Africa
    "ae": "/m/0j1z8", "uae": "/m/0j1z8",
    "il": "/m/03spz", "israel": "/m/03spz",
    "ma": "/m/04wgh", "morocco": "/m/04wgh",
    "eg": "/m/02k54", "egypt": "/m/02k54",
    "za": "/m/0hzlz", "south-africa": "/m/0hzlz",
    "ke": "/m/019rg5", "kenya": "/m/019rg5",
    "ru": "/m/06bnz", "russia": "/m/06bnz",
}

REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f172a; color: #e2e8f0; padding: 24px;
  }}
  .header {{ margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid #334155; }}
  .header h1 {{ font-size: 22px; color: #f8fafc; margin-bottom: 4px; }}
  .header .meta {{ font-size: 13px; color: #94a3b8; }}
  .header .meta span {{ margin-right: 16px; }}
  .summary {{ display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }}
  .card {{
    background: #1e293b; border-radius: 8px; padding: 10px 16px; border: 1px solid #334155; min-width: 120px;
  }}
  .card .label {{ font-size: 10px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
  .card .value {{ font-size: 18px; font-weight: 700; color: #4ade80; margin-top: 2px; }}
  .card .value.neutral {{ color: #e2e8f0; }}
  .filters {{
    background: #1e293b; border: 1px solid #334155; border-radius: 8px;
    padding: 12px 14px; margin-bottom: 14px;
  }}
  .filter-row {{
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;
  }}
  .filter-row:last-child {{ margin-bottom: 0; }}
  .filter-label {{
    font-size: 10px; color: #94a3b8; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.5px; min-width: 78px;
  }}
  .chip {{
    background: #334155; border: 1px solid #475569; border-radius: 14px;
    padding: 3px 11px; color: #cbd5e1; font-size: 12px; font-weight: 600;
    cursor: pointer; transition: all 0.15s; user-select: none; font-family: inherit;
  }}
  .chip:hover {{ border-color: #60a5fa; color: #fff; }}
  .chip.active {{ background: #1e40af; border-color: #3b82f6; color: #fff; }}
  .chip .badge {{
    background: rgba(255,255,255,0.25); border-radius: 10px;
    padding: 0 6px; font-size: 10px; margin-left: 4px;
  }}
  .range-input {{
    background: #0f172a; border: 1px solid #475569; border-radius: 6px;
    padding: 4px 8px; color: #e2e8f0; font-size: 12px; width: 118px; font-family: inherit;
  }}
  .range-input:focus {{ outline: 2px solid #3b82f6; border-color: transparent; }}
  .clear-btn {{
    background: transparent; border: 1px dashed #475569; border-radius: 6px;
    padding: 4px 10px; color: #94a3b8; font-size: 11px; cursor: pointer; font-family: inherit;
    margin-left: auto;
  }}
  .clear-btn:hover {{ border-color: #ef4444; color: #fca5a5; }}
  table {{
    width: 100%; border-collapse: collapse; font-size: 13px;
    background: #1e293b; border-radius: 8px; overflow: hidden;
  }}
  thead {{ background: #334155; }}
  th {{
    padding: 10px 12px; text-align: left; font-weight: 600; color: #cbd5e1;
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; white-space: nowrap;
    cursor: pointer; user-select: none;
  }}
  th.right {{ text-align: right; }}
  th.center {{ text-align: center; }}
  th:hover {{ background: #475569; color: #fff; }}
  th.sorted::after {{ content: attr(data-arrow); margin-left: 4px; color: #60a5fa; }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #1e293b; white-space: nowrap; }}
  td.right {{ text-align: right; }}
  td.center {{ text-align: center; }}
  td.price {{ color: #4ade80; font-weight: 700; text-align: right; }}
  td.date {{ color: #67e8f9; }}
  td.dim {{ color: #64748b; }}
  td.airline {{ color: #c4b5fd; }}
  td.best {{ color: #fbbf24; font-weight: 600; }}
  tr:nth-child(even) {{ background: #162032; }}
  tr:hover {{ background: #253350; }}
  tr.hidden-row {{ display: none; }}
  a {{ color: #60a5fa; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .stops-0 {{ color: #4ade80; }}
  .stops-1 {{ color: #fbbf24; }}
  .stops-2 {{ color: #fb923c; }}
  .footer {{
    margin-top: 14px; padding-top: 10px; border-top: 1px solid #334155;
    font-size: 12px; color: #64748b;
  }}
</style>
</head>
<body>
<div class="header">
  <h1>{title}</h1>
  <div class="meta">{meta}</div>
</div>
<div class="summary">{summary_cards}</div>
<div class="filters">{filters_html}</div>
<table id="rows-table">
<thead><tr>{thead}</tr></thead>
<tbody>{tbody}</tbody>
</table>
<div class="footer">{footer_info}</div>
<script>
const rows = Array.from(document.querySelectorAll('#rows-table tbody tr'));
const badgeVisible = document.getElementById('badge-visible');

function activeValues(cls) {{
  return new Set(Array.from(document.querySelectorAll('.chip.' + cls + '.active')).map(b => b.dataset.value));
}}

function applyFilters() {{
  const origins = activeValues('origin');
  const dests = activeValues('dest');
  const airlines = activeValues('airline');
  const stops = activeValues('stops');
  const pMinEl = document.getElementById('price-min');
  const pMaxEl = document.getElementById('price-max');
  const dMinEl = document.getElementById('date-min');
  const dMaxEl = document.getElementById('date-max');
  const pMin = pMinEl && pMinEl.value ? parseFloat(pMinEl.value) : -Infinity;
  const pMax = pMaxEl && pMaxEl.value ? parseFloat(pMaxEl.value) : Infinity;
  const dMin = dMinEl ? dMinEl.value : '';
  const dMax = dMaxEl ? dMaxEl.value : '';

  let visible = 0;
  rows.forEach(tr => {{
    const origin = tr.dataset.origin || '';
    const dest = tr.dataset.dest || '';
    const airline = tr.dataset.airline || '';
    const stopKey = tr.dataset.stopkey || '';
    const price = parseFloat(tr.dataset.price || 'NaN');
    const date = tr.dataset.date || '';

    const pass =
      (origins.size === 0 || origins.has(origin)) &&
      (dests.size === 0 || dests.has(dest)) &&
      (airlines.size === 0 || airlines.has(airline)) &&
      (stops.size === 0 || stops.has(stopKey)) &&
      (isNaN(price) || price >= pMin) &&
      (isNaN(price) || price <= pMax) &&
      (!dMin || !date || date >= dMin) &&
      (!dMax || !date || date <= dMax);

    tr.classList.toggle('hidden-row', !pass);
    if (pass) visible++;
  }});
  if (badgeVisible) badgeVisible.textContent = visible;
  renumber();
}}

function renumber() {{
  let i = 0;
  rows.forEach(tr => {{
    if (tr.classList.contains('hidden-row')) return;
    i++;
    const cell = tr.querySelector('td.idx');
    if (cell) cell.textContent = i;
  }});
}}

function toggleChip(el) {{ el.classList.toggle('active'); applyFilters(); }}

function clearAll() {{
  document.querySelectorAll('.chip.active').forEach(c => c.classList.remove('active'));
  ['price-min','price-max','date-min','date-max'].forEach(id => {{
    const el = document.getElementById(id); if (el) el.value = '';
  }});
  applyFilters();
}}

let currentSort = {{col: null, dir: 1}};
function sortBy(colIdx, type) {{
  const tbody = document.querySelector('#rows-table tbody');
  const dir = (currentSort.col === colIdx) ? -currentSort.dir : 1;
  currentSort = {{col: colIdx, dir: dir}};
  const arr = rows.slice();
  arr.sort((a, b) => {{
    const av = a.children[colIdx].dataset.sortkey || a.children[colIdx].textContent;
    const bv = b.children[colIdx].dataset.sortkey || b.children[colIdx].textContent;
    if (type === 'number') return ((parseFloat(av) || 0) - (parseFloat(bv) || 0)) * dir;
    return av.localeCompare(bv) * dir;
  }});
  arr.forEach(r => tbody.appendChild(r));
  document.querySelectorAll('th').forEach(th => {{ th.classList.remove('sorted'); th.removeAttribute('data-arrow'); }});
  const th = document.querySelectorAll('th')[colIdx];
  th.classList.add('sorted'); th.dataset.arrow = dir === 1 ? '↑' : '↓';
  renumber();
}}

document.addEventListener('DOMContentLoaded', () => {{
  ['price-min','price-max','date-min','date-max'].forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', applyFilters);
  }});
  applyFilters();
}});
</script>
</body>
</html>"""


PLACEHOLDER_KEY = "PASTE_YOUR_KEY_HERE"


def load_config() -> tuple[str, str]:
    """Return (api_key, default_currency). Guides the user through setup if the key is missing."""
    env_path = CACHE_DIR / ".env"

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not env_path.exists():
        env_path.write_text(f"SERPAPI_API_KEY={PLACEHOLDER_KEY}\n", encoding="utf-8")

    load_dotenv(env_path)
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key or api_key in (PLACEHOLDER_KEY, "your_api_key_here"):
        print(
            "SETUP REQUIRED: SerpApi key is not configured.\n"
            "\n"
            f"A placeholder file has been created at: {env_path}\n"
            "\n"
            "ASSISTANT: please guide the user through setup by doing the following:\n"
            "  1. Tell the user a free SerpApi key is required "
            "(free tier: 250 searches/month, 50/hour).\n"
            "  2. Offer to open https://serpapi.com/users/sign_up in the browser so "
            "they can sign up and copy the key from the dashboard.\n"
            "  3. Offer two options: (A) paste the key in chat and the assistant writes "
            f"it, or (B) the user edits {env_path} directly to replace "
            f"{PLACEHOLDER_KEY}.\n"
            "  4. Re-run the command that just failed.\n",
            file=sys.stderr,
        )
        sys.exit(1)

    default_currency = os.getenv("DEFAULT_CURRENCY", "USD").strip() or "USD"
    return api_key, default_currency


def format_price(price: float, currency: str) -> str:
    symbols = {"BRL": "R$", "USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency + " ")
    if currency == "BRL":
        return f"{symbol}{price:,.0f}".replace(",", ".")
    return f"{symbol}{price:,.0f}"


def format_duration(minutes: int) -> str:
    if not minutes:
        return "—"
    h, m = divmod(minutes, 60)
    return f"{h}h{m:02d}" if m else f"{h}h"


def cache_key(params: dict) -> str:
    filtered = {k: v for k, v in sorted(params.items()) if k != "api_key"}
    raw = json.dumps(filtered, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def cache_path(key: str) -> Path:
    return CACHE_DIR / f"{key}.json"


def cache_read(key: str, ttl_hours: int) -> dict | None:
    path = cache_path(key)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cached_at = datetime.fromisoformat(data["_cached_at"])
        if datetime.now() - cached_at > timedelta(hours=ttl_hours):
            return None
        print(f"  Cache hit ({cached_at.strftime('%Y-%m-%d %H:%M')})")
        return data["response"]
    except (json.JSONDecodeError, KeyError):
        return None


def cache_write(key: str, params: dict, response: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "_cached_at": datetime.now().isoformat(),
        "_params": {k: v for k, v in params.items() if k != "api_key"},
        "response": response,
    }
    cache_path(key).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def api_call(params: dict, use_cache: bool = True, ttl_hours: int = DEFAULT_CACHE_TTL_HOURS) -> tuple[dict, str, Path]:
    key = cache_key(params)
    cfile = cache_path(key)

    if use_cache:
        cached = cache_read(key, ttl_hours)
        if cached is not None:
            return cached, "hit", cfile

    response = requests.get(SERPAPI_URL, params=params, timeout=30)
    if response.status_code != 200:
        print(f"API error ({response.status_code}): {response.text[:500]}")
        sys.exit(1)
    data = response.json()
    if "error" in data:
        print(f"SerpApi error: {data['error']}")
        sys.exit(1)

    cache_write(key, params, data)
    return data, "miss", cfile


def write_html(filename: str, html: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(html, encoding="utf-8")
    return path


def stops_class(n: int) -> str:
    return f"stops-{min(n, 3)}"


def resolve_area(value: str) -> str:
    key = value.lower()
    if key in AREA_MAP:
        return AREA_MAP[key]
    if key.startswith("/m/") or key.startswith("/g/"):
        return value
    print(f"Unknown area: {value}")
    print(f"Available areas: {', '.join(sorted(set(AREA_MAP.keys())))}")
    sys.exit(1)


def parse_stops(value: str) -> int:
    k = value.lower()
    if k in STOPS_MAP:
        return STOPS_MAP[k]
    if k.isdigit():
        return int(k)
    print(f"Invalid --stops value: {value}. Use: any, nonstop, 1, 2")
    sys.exit(1)


def parse_duration(value: str) -> int:
    k = value.lower()
    if k in DURATION_MAP:
        return DURATION_MAP[k]
    if k.isdigit():
        return int(k)
    print(f"Invalid --duration value: {value}. Use: weekend, 1week, 2weeks")
    sys.exit(1)


def parse_class(value: str) -> int:
    k = value.lower()
    if k in CLASS_MAP:
        return CLASS_MAP[k]
    print(f"Invalid --class value: {value}. Use: economy, premium, business, first")
    sys.exit(1)


def parse_interest(value: str) -> str:
    k = value.lower()
    if k in INTEREST_MAP:
        return INTEREST_MAP[k]
    if k.startswith("/m/") or k.startswith("/g/"):
        return value
    print(f"Unknown --interest: {value}. Known: {', '.join(INTEREST_MAP)} (or pass a raw KGID)")
    sys.exit(1)


def parse_travel_mode(value: str) -> int:
    k = value.lower()
    if k in TRAVEL_MODE_MAP:
        return TRAVEL_MODE_MAP[k]
    print(f"Invalid --travel-mode value: {value}. Use: all, flight")
    sys.exit(1)


def parse_sort_by(value: str) -> int:
    k = value.lower()
    if k in SORT_BY_MAP:
        return SORT_BY_MAP[k]
    print(f"Invalid --sort-by value: {value}. Use: {', '.join(SORT_BY_MAP)}")
    sys.exit(1)


def parse_layover_range(value: str) -> str:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        print("Invalid --layover value. Use: 'min_minutes,max_minutes' (e.g., 90,330)")
        sys.exit(1)
    return ",".join(parts)


def parse_times(value: str) -> str:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) not in (2, 4) or not all(p.isdigit() and 0 <= int(p) <= 23 for p in parts):
        print("Invalid times value. Use 2 or 4 hours in 0-23, e.g., '4,18' or '4,18,3,19'")
        sys.exit(1)
    return ",".join(parts)


def build_explore_params(origin: str, args: argparse.Namespace, api_key: str) -> dict:
    """Build API params for a single origin explore call."""
    if args.interest and args.travel_mode and parse_travel_mode(args.travel_mode) == 1:
        print("--interest and --travel-mode flight are mutually exclusive.")
        sys.exit(1)
    if args.include_airlines and args.exclude_airlines:
        print("--include-airlines and --exclude-airlines are mutually exclusive.")
        sys.exit(1)

    params = {
        "engine": "google_travel_explore",
        "departure_id": origin,
        "currency": args.currency,
        "hl": args.hl,
        "gl": args.gl,
        "api_key": api_key,
    }
    if args.to:
        params["arrival_id"] = args.to
    if args.area:
        params["arrival_area_id"] = resolve_area(args.area)
    if args.depart:
        params["outbound_date"] = args.depart
    if args.return_date:
        params["return_date"] = args.return_date
    if args.month is not None:
        if args.month > 0:
            now = datetime.now()
            valid_months = {((now.month - 1 + i) % 12) + 1 for i in range(6)}
            if args.month not in valid_months:
                valid_list = sorted(valid_months)
                print(
                    f"--month {args.month} is outside SerpApi's explore window. "
                    f"The engine only accepts the next 6 months from today "
                    f"({now.strftime('%Y-%m')}): {valid_list}. "
                    f"For months beyond that, use `search` with specific dates instead."
                )
                sys.exit(1)
        params["month"] = args.month
    if args.duration:
        params["travel_duration"] = parse_duration(args.duration)
    if args.stops:
        params["stops"] = parse_stops(args.stops)
    if args.max_price:
        params["max_price"] = args.max_price
    if args.max_duration:
        params["max_duration"] = args.max_duration
    if args.interest:
        params["interest"] = parse_interest(args.interest)
    if args.travel_mode:
        params["travel_mode"] = parse_travel_mode(args.travel_mode)
    if args.travel_class:
        params["travel_class"] = parse_class(args.travel_class)
    if args.oneway:
        params["type"] = 2
    if args.include_airlines:
        params["include_airlines"] = args.include_airlines
    if args.exclude_airlines:
        params["exclude_airlines"] = args.exclude_airlines
    if args.bags:
        params["bags"] = args.bags
    if args.adults and args.adults > 1:
        params["adults"] = args.adults
    if args.children:
        params["children"] = args.children
    if args.infants_on_lap:
        params["infants_on_lap"] = args.infants_on_lap
    if args.infants_in_seat:
        params["infants_in_seat"] = args.infants_in_seat
    return params


def build_search_params(args: argparse.Namespace, api_key: str) -> dict:
    """Build API params for a google_flights search."""
    if args.include_airlines and args.exclude_airlines:
        print("--include-airlines and --exclude-airlines are mutually exclusive.")
        sys.exit(1)

    params = {
        "engine": "google_flights",
        "currency": args.currency,
        "hl": args.hl,
        "gl": args.gl,
        "api_key": api_key,
    }

    if args.multi_city_json:
        # Validate it is a JSON array and pass through as a string.
        try:
            legs = json.loads(args.multi_city_json)
            if not isinstance(legs, list) or not legs:
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            print("--multi-city-json must be a non-empty JSON array of legs.")
            sys.exit(1)
        params["type"] = 3
        params["multi_city_json"] = args.multi_city_json
    else:
        if not args.origin or not args.to or not args.depart:
            print("search requires --from, --to, --depart (or use --multi-city-json).")
            sys.exit(1)
        params["departure_id"] = args.origin
        params["arrival_id"] = args.to
        params["outbound_date"] = args.depart
        if args.oneway:
            params["type"] = 2
        else:
            params["type"] = 1
            if args.return_date:
                params["return_date"] = args.return_date

    if args.stops:
        params["stops"] = parse_stops(args.stops)
    if args.max_price:
        params["max_price"] = args.max_price
    if args.max_duration:
        params["max_duration"] = args.max_duration
    if args.travel_class:
        params["travel_class"] = parse_class(args.travel_class)
    if args.include_airlines:
        params["include_airlines"] = args.include_airlines
    if args.exclude_airlines:
        params["exclude_airlines"] = args.exclude_airlines
    if args.adults and args.adults > 1:
        params["adults"] = args.adults
    if args.children:
        params["children"] = args.children
    if args.infants_on_lap:
        params["infants_on_lap"] = args.infants_on_lap
    if args.infants_in_seat:
        params["infants_in_seat"] = args.infants_in_seat
    if args.bags:
        params["bags"] = args.bags
    if args.outbound_times:
        params["outbound_times"] = parse_times(args.outbound_times)
    if args.return_times:
        params["return_times"] = parse_times(args.return_times)
    if args.low_emissions:
        params["emissions"] = 1
    if args.layover:
        params["layover_duration"] = parse_layover_range(args.layover)
    if args.exclude_conns:
        params["exclude_conns"] = args.exclude_conns
    if args.sort_by:
        params["sort_by"] = parse_sort_by(args.sort_by)
    if args.exclude_basic:
        params["exclude_basic"] = "true"
    if args.deep_search:
        params["deep_search"] = "true"
    return params


def collect_flights(data: dict) -> list[dict]:
    """Normalize any flight-like response into a flat list of flight options."""
    best = data.get("best_flights", []) or []
    other = data.get("other_flights", []) or []
    if best or other:
        return best + other
    flights = data.get("flights", []) or []
    return flights


def cmd_explore(args: argparse.Namespace) -> None:
    api_key, default_currency = load_config()
    if args.currency is None:
        args.currency = default_currency

    origins = [o.strip().upper() for o in args.origin.split(",")]
    cache_files: list[Path] = []
    total = 0

    for origin in origins:
        params = build_explore_params(origin, args, api_key)
        label = f"{origin} → {args.to}" if args.to else f"from {origin}"
        print(f"Searching {label}...")
        data, ci, cfile = api_call(params, use_cache=not args.no_cache, ttl_hours=args.cache_ttl)
        cache_files.append(cfile)
        count = len(data.get("destinations") or []) + len(collect_flights(data)) + len(data.get("flights") or [])
        total += count
        print(f"  {count} result(s) ({ci})")

    if total == 0:
        print("No results.")
        return

    for cf in cache_files:
        print(f"  Data:  {cf}")
    print()
    print("To build a consolidated HTML dashboard, run:")
    print(f"  search.py report {' '.join(str(cf) for cf in cache_files)}")


def cmd_search(args: argparse.Namespace) -> None:
    api_key, default_currency = load_config()
    if args.currency is None:
        args.currency = default_currency

    params = build_search_params(args, api_key)

    if args.multi_city_json:
        label = "multi-city"
        origin, dest = "(multi)", "(multi)"
    else:
        origin, dest = args.origin, args.to
        label = "one-way" if args.oneway else "round trip"
    print(f"Searching flights ({label}) {origin} → {dest}...")

    data, cache_info, cache_file = api_call(params, use_cache=not args.no_cache, ttl_hours=args.cache_ttl)

    flights = collect_flights(data)
    if not flights:
        print("No flights found.")
        return

    print(f"  {len(flights)} options found ({cache_info})")
    print(f"  Data:  {cache_file}")
    print()
    print("To build a consolidated HTML dashboard, run:")
    print(f"  search.py report {cache_file}")


# ---- report helpers -----------------------------------------------------------

def resolve_cache_spec(spec: str) -> Path:
    """Accept a full path or a bare hash; return the resolved Path."""
    p = Path(spec)
    if p.exists():
        return p.resolve()
    hp = CACHE_DIR / f"{spec}.json"
    if hp.exists():
        return hp.resolve()
    print(f"Cache not found: {spec}", file=sys.stderr)
    sys.exit(1)


def _safe_int(v) -> int:
    try:
        return int(v or 0)
    except (TypeError, ValueError):
        return 0


def _explore_dest_to_row(d: dict, origin: str, currency: str) -> dict:
    """google_travel_explore destinations[] shape."""
    airport = (d.get("destination_airport") or {}).get("code") or ""
    start = d.get("start_date") or ""
    end = d.get("end_date") or ""
    days = ""
    if start and end:
        try:
            days = str((datetime.strptime(end, "%Y-%m-%d") - datetime.strptime(start, "%Y-%m-%d")).days)
        except ValueError:
            pass
    return {
        "type": "explore",
        "origin": origin,
        "dest": airport,
        "city": d.get("name") or "",
        "country": d.get("country") or "",
        "price": d.get("flight_price"),
        "currency": currency,
        "depart_date": start,
        "return_date": end,
        "days": days,
        "duration_min": _safe_int(d.get("flight_duration")),
        "stops": _safe_int(d.get("number_of_stops")),
        "airline": d.get("airline") or "",
        "departure_time": "",
        "arrival_time": "",
        "co2_kg": None,
        "link": d.get("link") or "",
        "is_best": False,
    }


def _explore_flight_to_row(
    f: dict,
    origin: str,
    dest: str,
    currency: str,
    start_date: str = "",
    fallback_link: str = "",
) -> dict:
    """google_travel_explore flight schema: duration, number_of_stops, airline string.

    The `start_date` (window start) and `google_flights_link` deep-link live at the
    top level of the response, not on each flight object — the caller passes them
    in so they show up as the flight's depart date and link. `end_date` is NOT
    propagated because it represents the end of the flexible window, not a booked
    return; showing it would wrongly imply a round-trip itinerary.
    """
    return {
        "type": "explore-route",
        "origin": origin,
        "dest": dest,
        "city": "",
        "country": "",
        "price": f.get("price"),
        "currency": currency,
        "depart_date": f.get("departure_date") or f.get("start_date") or start_date,
        # Only use explicit per-flight return_date. The top-level end_date is the
        # end of the flexible window, not a booked return, so we do not inherit it.
        "return_date": f.get("return_date") or "",
        "days": "",
        "duration_min": _safe_int(f.get("duration")),
        "stops": _safe_int(f.get("number_of_stops")),
        "airline": f.get("airline") or "",
        "departure_time": "",
        "arrival_time": "",
        "co2_kg": None,
        "link": f.get("google_flights_link") or f.get("link") or fallback_link,
        "is_best": bool(f.get("cheapest_flight")),
    }


def _search_flight_to_row(f: dict, origin_fb: str, dest_fb: str, currency: str, fallback_link: str) -> dict:
    """google_flights flight schema: nested segments, total_duration."""
    segs = f.get("flights") or []
    airlines = list(dict.fromkeys(s.get("airline") or "" for s in segs if s.get("airline")))
    first = segs[0] if segs else {}
    last = segs[-1] if segs else {}
    dep_ap = first.get("departure_airport") or {}
    arr_ap = last.get("arrival_airport") or {}
    dep_full = dep_ap.get("time") or ""
    arr_full = arr_ap.get("time") or ""
    depart_date = dep_full.split(" ", 1)[0] if " " in dep_full else ""
    dep_time = dep_full.split(" ", 1)[1] if " " in dep_full else dep_full
    arr_time = arr_full.split(" ", 1)[1] if " " in arr_full else arr_full
    co2 = (f.get("carbon_emissions") or {}).get("this_flight")
    return {
        "type": "search",
        "origin": dep_ap.get("id") or origin_fb,
        "dest": arr_ap.get("id") or dest_fb,
        "city": "",
        "country": "",
        "price": f.get("price"),
        "currency": currency,
        "depart_date": depart_date,
        "return_date": "",
        "days": "",
        "duration_min": _safe_int(f.get("total_duration")),
        "stops": max(len(segs) - 1, 0),
        "airline": ", ".join(airlines),
        "departure_time": dep_time,
        "arrival_time": arr_time,
        "co2_kg": (co2 // 1000) if co2 else None,
        "link": fallback_link,
        "is_best": False,
    }


def cache_to_rows(cache_entry: dict) -> list[dict]:
    params = cache_entry.get("_params") or {}
    response = cache_entry.get("response") or {}
    engine = params.get("engine")
    origin = (params.get("departure_id") or "").upper()
    dest = (params.get("arrival_id") or "").upper()
    currency = params.get("currency") or "USD"
    rows: list[dict] = []

    if engine == "google_travel_explore":
        for d in response.get("destinations") or []:
            rows.append(_explore_dest_to_row(d, origin, currency))
        # Route mode (arrival_id set): window start and the deep-link are top-level.
        # We intentionally do not propagate end_date because on a flight item it
        # would be misread as a booked return.
        exp_start = response.get("start_date") or ""
        exp_link = response.get("google_flights_link") or ""
        for f in response.get("flights") or []:
            rows.append(_explore_flight_to_row(f, origin, dest, currency, exp_start, exp_link))
        for f in response.get("best_flights") or []:
            r = _explore_flight_to_row(f, origin, dest, currency, exp_start, exp_link)
            r["is_best"] = True
            rows.append(r)
        for f in response.get("other_flights") or []:
            rows.append(_explore_flight_to_row(f, origin, dest, currency, exp_start, exp_link))
    elif engine == "google_flights":
        fallback_link = (response.get("search_metadata") or {}).get("google_flights_url", "")
        for f in response.get("best_flights") or []:
            r = _search_flight_to_row(f, origin, dest, currency, fallback_link)
            r["is_best"] = True
            rows.append(r)
        for f in response.get("other_flights") or []:
            rows.append(_search_flight_to_row(f, origin, dest, currency, fallback_link))
        for f in response.get("flights") or []:
            rows.append(_search_flight_to_row(f, origin, dest, currency, fallback_link))

    return rows


def _chips_html(cls: str, values: list[str], counts: dict) -> str:
    return "".join(
        f'<button class="chip {cls}" data-value="{v}" onclick="toggleChip(this)">'
        f'{v} <span class="badge">{counts.get(v, 0)}</span></button>'
        for v in values
    )


def render_report_html(rows: list[dict], title: str, sources: list[dict]) -> str:
    currencies = [r["currency"] for r in rows if r.get("currency")]
    currency = max(set(currencies), key=currencies.count) if currencies else "USD"
    prices = [r["price"] for r in rows if isinstance(r.get("price"), (int, float))]
    lowest = format_price(min(prices), currency) if prices else "—"
    highest = format_price(max(prices), currency) if prices else "—"

    unique_origins = sorted({r["origin"] for r in rows if r.get("origin")})
    unique_dests = sorted({r["dest"] for r in rows if r.get("dest")})
    unique_airlines = sorted({
        a.strip() for r in rows for a in (r["airline"].split(",") if r.get("airline") else []) if a.strip()
    })

    origin_counts = {o: sum(1 for r in rows if r["origin"] == o) for o in unique_origins}
    dest_counts = {d: sum(1 for r in rows if r["dest"] == d) for d in unique_dests}
    airline_counts = {
        a: sum(1 for r in rows if a in (r.get("airline") or "")) for a in unique_airlines
    }

    summary_cards = (
        f'<div class="card"><div class="label">Lowest price</div><div class="value">{lowest}</div></div>'
        f'<div class="card"><div class="label">Highest price</div><div class="value">{highest}</div></div>'
        f'<div class="card"><div class="label">Options</div><div class="value neutral">{len(rows)}</div></div>'
        f'<div class="card"><div class="label">Visible</div><div class="value neutral" id="badge-visible">{len(rows)}</div></div>'
        f'<div class="card"><div class="label">Origins</div><div class="value neutral">{len(unique_origins)}</div></div>'
        f'<div class="card"><div class="label">Destinations</div><div class="value neutral">{len(unique_dests)}</div></div>'
    )

    stops_chips = (
        '<button class="chip stops" data-value="0" onclick="toggleChip(this)">Nonstop</button>'
        '<button class="chip stops" data-value="1" onclick="toggleChip(this)">1 stop</button>'
        '<button class="chip stops" data-value="2" onclick="toggleChip(this)">2+ stops</button>'
    )

    filters_html = (
        '<div class="filter-row"><span class="filter-label">Origin</span>'
        f'{_chips_html("origin", unique_origins, origin_counts)}</div>'
        '<div class="filter-row"><span class="filter-label">Destination</span>'
        f'{_chips_html("dest", unique_dests, dest_counts)}</div>'
        '<div class="filter-row"><span class="filter-label">Airline</span>'
        f'{_chips_html("airline", unique_airlines, airline_counts)}</div>'
        '<div class="filter-row"><span class="filter-label">Stops</span>'
        f'{stops_chips}</div>'
        '<div class="filter-row">'
        '<span class="filter-label">Price</span>'
        '<input class="range-input" id="price-min" type="number" placeholder="min">'
        '<input class="range-input" id="price-max" type="number" placeholder="max">'
        '<span class="filter-label" style="min-width: 50px;">Date</span>'
        '<input class="range-input" id="date-min" type="date">'
        '<input class="range-input" id="date-max" type="date">'
        '<button class="clear-btn" onclick="clearAll()">Clear all</button>'
        '</div>'
    )

    cols = [
        ("#", "", "number"),
        ("Type", "center", "string"),
        ("Origin", "", "string"),
        ("Dest", "", "string"),
        ("City", "", "string"),
        ("Country", "", "string"),
        ("Price", "right", "number"),
        ("Depart", "", "string"),
        ("Return", "", "string"),
        ("Duration", "", "number"),
        ("Stops", "center", "number"),
        ("Airline", "", "string"),
        ("Dep", "", "string"),
        ("Arr", "", "string"),
        ("CO₂", "right", "number"),
        ("Link", "center", "string"),
    ]
    thead = "".join(
        f'<th class="{a}" onclick="sortBy({i}, \'{t}\')">{name}</th>'
        for i, (name, a, t) in enumerate(cols)
    )

    def _row_html(i: int, r: dict) -> str:
        stopkey = "0" if r["stops"] == 0 else ("1" if r["stops"] == 1 else "2")
        airline_key = (r["airline"].split(",")[0].strip()) if r.get("airline") else ""
        price = r.get("price")
        price_str = format_price(price, r["currency"]) if isinstance(price, (int, float)) else "—"
        link_html = f'<a href="{r["link"]}" target="_blank">Google</a>' if r.get("link") else "—"
        co2_str = f"{r['co2_kg']}kg" if r.get("co2_kg") else "—"
        type_label = "Best" if r["is_best"] else r["type"]
        type_cls = "best" if r["is_best"] else "dim"
        price_sort = price if isinstance(price, (int, float)) else 0
        return (
            f'<tr data-origin="{r["origin"]}" data-dest="{r["dest"]}" '
            f'data-airline="{airline_key}" data-stopkey="{stopkey}" '
            f'data-price="{price_sort if isinstance(price, (int, float)) else ""}" '
            f'data-date="{r["depart_date"]}">'
            f'<td class="idx dim" data-sortkey="{i}">{i}</td>'
            f'<td class="center {type_cls}" data-sortkey="{type_label}">{type_label}</td>'
            f'<td class="dim" data-sortkey="{r["origin"]}">{r["origin"] or "—"}</td>'
            f'<td class="dim" data-sortkey="{r["dest"]}">{r["dest"] or "—"}</td>'
            f'<td data-sortkey="{r["city"]}">{r["city"] or "—"}</td>'
            f'<td data-sortkey="{r["country"]}">{r["country"] or "—"}</td>'
            f'<td class="price" data-sortkey="{price_sort}">{price_str}</td>'
            f'<td class="date" data-sortkey="{r["depart_date"]}">{r["depart_date"] or "—"}</td>'
            f'<td class="date" data-sortkey="{r["return_date"]}">{r["return_date"] or "—"}</td>'
            f'<td data-sortkey="{r["duration_min"]}">{format_duration(r["duration_min"])}</td>'
            f'<td class="center {stops_class(r["stops"])}" data-sortkey="{r["stops"]}">{r["stops"]}</td>'
            f'<td class="airline" data-sortkey="{r["airline"]}">{r["airline"] or "—"}</td>'
            f'<td class="date" data-sortkey="{r["departure_time"]}">{r["departure_time"] or "—"}</td>'
            f'<td class="date" data-sortkey="{r["arrival_time"]}">{r["arrival_time"] or "—"}</td>'
            f'<td class="right dim" data-sortkey="{r["co2_kg"] or 0}">{co2_str}</td>'
            f'<td class="center">{link_html}</td>'
            f'</tr>'
        )

    def _sortkey(r: dict) -> float:
        p = r.get("price")
        return float(p) if isinstance(p, (int, float)) else 1e12
    sorted_rows = sorted(rows, key=_sortkey)
    tbody = "\n".join(_row_html(i + 1, r) for i, r in enumerate(sorted_rows))

    source_parts = []
    for s in sources:
        eng = s["engine"].replace("google_", "")
        lbl = s["origin"]
        if s.get("dest"):
            lbl += f"→{s['dest']}"
        source_parts.append(f"{eng} ({lbl})")
    meta = (
        f'<span>Sources: <strong>{len(sources)}</strong></span>'
        f'<span>Currency: <strong>{currency}</strong></span>'
        f'<span>{", ".join(source_parts)}</span>'
    )

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    footer_info = f"Generated at {now_str} — {len(sources)} source(s), {len(rows)} row(s)"

    return REPORT_TEMPLATE.format(
        title=title,
        meta=meta,
        summary_cards=summary_cards,
        filters_html=filters_html,
        thead=thead,
        tbody=tbody,
        footer_info=footer_info,
    )


def cmd_report(args: argparse.Namespace) -> None:
    if not args.inputs:
        print("report: provide at least one cache path or hash", file=sys.stderr)
        sys.exit(1)

    paths = [resolve_cache_spec(s) for s in args.inputs]
    rows: list[dict] = []
    sources: list[dict] = []

    for p in paths:
        try:
            entry = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Failed to read {p}: {e}", file=sys.stderr)
            sys.exit(1)
        rows.extend(cache_to_rows(entry))
        params = entry.get("_params") or {}
        sources.append({
            "engine": params.get("engine", "?"),
            "origin": (params.get("departure_id") or "").upper(),
            "dest": (params.get("arrival_id") or "").upper(),
            "path": p,
        })

    if not rows:
        print("report: no rows extracted from the inputs.", file=sys.stderr)
        sys.exit(1)

    title = args.title or f"Flight Search Report — {len(rows)} options from {len(paths)} searches"
    html = render_report_html(rows, title=title, sources=sources)

    if args.output:
        out = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = OUTPUT_DIR / f"report_{ts}.html"
    if not out.is_absolute():
        out = (OUTPUT_DIR / out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    print(f"Report: {out}")
    print(f"  {len(rows)} option(s) from {len(paths)} cache file(s)")


def add_common_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--currency", default=None, help="Currency (default: $DEFAULT_CURRENCY or USD)")
    p.add_argument("--hl", default="en", help="Response language (default: en)")
    p.add_argument("--gl", default="us", help="Country localization (default: us)")
    p.add_argument("--limit", type=int, help="Limit number of result rows")
    p.add_argument("--adults", type=int, default=1, help="Adults (default: 1)")
    p.add_argument("--children", type=int, default=0, help="Children")
    p.add_argument("--infants-on-lap", type=int, default=0, help="Infants on lap")
    p.add_argument("--infants-in-seat", type=int, default=0, help="Infants with a seat")
    p.add_argument("--no-cache", action="store_true", help="Bypass cache and force a fresh search")
    p.add_argument("--cache-ttl", type=int, default=DEFAULT_CACHE_TTL_HOURS, help=f"Cache TTL in hours (default: {DEFAULT_CACHE_TTL_HOURS})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Google Flights Search via SerpApi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s explore --from JFK
  %(prog)s explore --from JFK --month 7 --stops nonstop --interest beaches
  %(prog)s explore --from GRU --to LIS --month 7 --stops nonstop
  %(prog)s search --from JFK --to LIS --depart 2026-05-15 --return 2026-05-22
  %(prog)s search --from JFK --to LIS --depart 2026-05-15 --oneway --sort-by price
  %(prog)s report <cache_file_or_hash> [<cache_file_or_hash> ...]

explore/search only write cache JSON. Use `report` to consolidate one or more cache
files into a single filterable HTML dashboard.
        """,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- explore ---
    p_explore = subparsers.add_parser("explore", help="Discover cheap destinations / flexible-date route")
    p_explore.add_argument("--from", dest="origin", required=True, help="Origin airport (IATA) — comma-separated for multiple")
    p_explore.add_argument("--to", help="Destination airport (IATA or KGID). Omit for anywhere; with a single origin, enables flexible-date mode for the route.")
    p_explore.add_argument("--area", help="Arrival region/country filter (e.g. europe, south-america, br, pt)")
    p_explore.add_argument("--depart", help="Specific departure date (YYYY-MM-DD)")
    p_explore.add_argument("--return", dest="return_date", help="Specific return date (YYYY-MM-DD)")
    p_explore.add_argument("--month", type=int, choices=range(0, 13), help="Month (1-12); 0 = any of the next 6 months. SerpApi rejects months beyond the next 6 from today; use `search` with specific dates for farther-out months.")
    p_explore.add_argument("--duration", help="Flexible duration: weekend, 1week, 2weeks")
    p_explore.add_argument("--stops", help="Stops: any, nonstop, 1, 2")
    p_explore.add_argument("--max-price", type=int, help="Maximum flight price")
    p_explore.add_argument("--max-duration", type=int, help="Maximum flight duration in minutes")
    p_explore.add_argument("--interest", help="Interest: beaches, outdoors, museums, history, skiing (or raw KGID). Mutually exclusive with --travel-mode flight.")
    p_explore.add_argument("--travel-mode", help="Travel mode: all (default), flight. Mutually exclusive with --interest.")
    p_explore.add_argument("--class", dest="travel_class", help="Cabin class: economy, premium, business, first")
    p_explore.add_argument("--oneway", action="store_true", help="One-way only (type=2)")
    p_explore.add_argument("--include-airlines", help="Only these airlines (comma-separated IATA or alliance: STAR_ALLIANCE, SKYTEAM, ONEWORLD)")
    p_explore.add_argument("--exclude-airlines", help="Exclude these airlines (comma-separated IATA or alliance)")
    p_explore.add_argument("--bags", type=int, help="Carry-on bags")
    add_common_flags(p_explore)
    p_explore.set_defaults(func=cmd_explore)

    # --- search ---
    p_search = subparsers.add_parser("search", help="Search a specific route (exact dates)")
    p_search.add_argument("--from", dest="origin", help="Origin airport IATA")
    p_search.add_argument("--to", help="Destination airport IATA")
    p_search.add_argument("--depart", help="Departure date (YYYY-MM-DD)")
    p_search.add_argument("--return", dest="return_date", help="Return date (YYYY-MM-DD)")
    p_search.add_argument("--oneway", action="store_true", help="One-way only")
    p_search.add_argument("--multi-city-json", help='Multi-city JSON array, e.g. \'[{"departure_id":"JFK","arrival_id":"LIS","date":"2026-05-15"},{"departure_id":"LIS","arrival_id":"MAD","date":"2026-05-20"}]\'. Sets type=3 and ignores --from/--to/--depart/--return.')
    p_search.add_argument("--stops", help="Stops: any, nonstop, 1, 2")
    p_search.add_argument("--max-price", type=int, help="Maximum price")
    p_search.add_argument("--max-duration", type=int, help="Maximum duration in minutes")
    p_search.add_argument("--class", dest="travel_class", help="Cabin class: economy, premium, business, first")
    p_search.add_argument("--include-airlines", help="Only these airlines (comma-separated IATA or alliance)")
    p_search.add_argument("--exclude-airlines", help="Exclude these airlines (comma-separated IATA or alliance)")
    p_search.add_argument("--bags", type=int, help="Carry-on bags")
    p_search.add_argument("--outbound-times", help="Outbound time window, hours 0-23: 'depStart,depEnd' or 'depStart,depEnd,arrStart,arrEnd'")
    p_search.add_argument("--return-times", help="Return time window, same format as --outbound-times")
    p_search.add_argument("--low-emissions", action="store_true", help="Show only lower-emission options")
    p_search.add_argument("--layover", help="Layover duration range in minutes: 'min,max' (e.g., 90,330)")
    p_search.add_argument("--exclude-conns", help="Comma-separated connecting airport IATA codes to exclude")
    p_search.add_argument("--sort-by", help="Sort: top, price, departure, arrival, duration, emissions")
    p_search.add_argument("--exclude-basic", action="store_true", help="Exclude basic economy (US domestic only)")
    p_search.add_argument("--deep-search", action="store_true", help="Thorough (slower) search")
    add_common_flags(p_search)
    p_search.set_defaults(func=cmd_search)

    # --- report ---
    p_report = subparsers.add_parser(
        "report",
        help="Consolidate one or more cache files into a single filterable HTML dashboard",
    )
    p_report.add_argument(
        "inputs",
        nargs="+",
        help="Cache paths (~/.flight-search/<hash>.json) or bare hashes",
    )
    p_report.add_argument("--output", help="Output HTML path (default: ~/.flight-search/output/report_<ts>.html)")
    p_report.add_argument("--title", help="Custom title for the report")
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
