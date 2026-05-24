# Refactor Stage 3-4 Implementation Notes

This document records the Streamlit application split.

## Scope

Implemented:

1. Stage 3: Split Streamlit UI into app shell, page modules, and reusable components.
2. Stage 4: Make root `app.py` a thin backward-compatible entrypoint.

Not implemented yet:

- legacy script archival
- backtest engine rewrite
- root README rewrite
- full app test automation

## Why This Refactor Was Needed

Before this stage:

- `app.py` contained routing, page rendering, data loading, strategy execution, sentiment display, export logic, and risk metrics.
- `src/ui/components.py` contained CSS, sidebar controls, cards, forms, home page rendering, and other shared UI.

That made the app harder to navigate and harder to extend.

After this stage:

- root `app.py` only delegates to the Streamlit package app.
- one major page lives in one file.
- reusable UI components live in component modules.
- routing is isolated.

## New Streamlit Structure

Created:

```text
src/quant_research/apps/streamlit/
├── __init__.py
├── main.py
├── router.py
├── components/
│   ├── __init__.py
│   ├── cards.py
│   ├── forms.py
│   ├── layout.py
│   ├── sidebar.py
│   └── styles.py
├── pages/
│   ├── __init__.py
│   ├── export.py
│   ├── home.py
│   ├── market_data.py
│   ├── risk_metrics.py
│   ├── sentiment.py
│   └── strategy_lab.py
└── state/
    └── __init__.py
```

## File Responsibilities

### Root Entrypoint

```text
app.py
```

Now only contains:

```python
from src.quant_research.apps.streamlit.main import main

if __name__ == "__main__":
    main()
```

This preserves:

```bash
streamlit run app.py
```

### App Shell

```text
src/quant_research/apps/streamlit/main.py
```

Owns:

- app initialization
- page config
- CSS loading
- header rendering
- sidebar rendering
- app-level data loading
- calling the router

### Router

```text
src/quant_research/apps/streamlit/router.py
```

Owns:

- mapping the selected navigation page to the correct page renderer
- data-required gating for pages that need market data

### Pages

Each page exposes one obvious render function.

| Page module | Main function |
|---|---|
| `pages/home.py` | `render_home_page(...)` |
| `pages/market_data.py` | `render_market_data_page(...)` |
| `pages/strategy_lab.py` | `render_strategy_lab_page(...)` |
| `pages/risk_metrics.py` | `render_volatility_page(...)`, `render_risk_metrics_page(...)` |
| `pages/sentiment.py` | `render_sentiment_page(...)` |
| `pages/export.py` | `render_export_page(...)` |

### Components

| Component module | Responsibility |
|---|---|
| `components/styles.py` | page config and CSS |
| `components/sidebar.py` | navigation and market-data form |
| `components/layout.py` | header, data summary, empty state |
| `components/cards.py` | KPI/card helpers |
| `components/forms.py` | MA, RSI, volatility, sentiment controls |

## Compatibility Preserved

The old UI module remains as a compatibility wrapper:

```text
src/ui/components.py
```

It re-exports the new component/page functions so old imports do not immediately break.

## Behavior Changes

No intentional product behavior changes.

The refactor preserved:

- Home page
- sidebar navigation
- market data page
- Strategy Lab
- Risk & Metrics
- Sentiment
- Export
- current backtest behavior
- root `streamlit run app.py` workflow

Small cleanup included:

- replaced deprecated `use_container_width=True` calls in the newly split Streamlit modules with `width="stretch"`.

## Validation Commands Run

```bash
python3 -m compileall -q src/quant_research/apps/streamlit/components
.venv/bin/python -c "from src.quant_research.apps.streamlit.components.sidebar import render_sidebar_inputs; from src.quant_research.apps.streamlit.components.styles import load_custom_css; print('components import ok')"

python3 -m compileall -q src/quant_research/apps/streamlit
.venv/bin/python -c "from src.quant_research.apps.streamlit.router import render_current_page; from src.quant_research.apps.streamlit.pages.strategy_lab import render_strategy_lab_page; print('pages import ok')"

python3 -m compileall -q app.py src tests
.venv/bin/python -c "import app; print('app import ok')"
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -c "import app; from src.quant_research.apps.streamlit.main import main; print('app imports ok')"
curl -I http://localhost:8502
```

Result:

```text
Ran 5 tests
OK
HTTP/1.1 200 OK
```

## Current Risk

Medium-low.

The app was structurally split, but compatibility wrappers and root entrypoint preservation reduce risk. No quant calculations were intentionally changed.

## Manual Checks Still Recommended

Open:

```text
http://localhost:8502
```

Check:

- sidebar opens and closes
- Home renders without loaded data
- load AAPL daily data
- Market Data page renders
- Strategy Lab page renders MA and RSI controls
- Risk & Metrics page renders volatility and stats
- Sentiment page renders
- Export page renders and downloads CSV

## Next Recommended Stage

Stage 5 should archive legacy scripts and generated outputs:

```text
src/backtest.py
src/rsi.py
src/movingAverage.py
src/fetch_data.py
src/fetch_data_yf.py
src/trade_log.csv
src/trade_log_rsi.csv
```

Recommended destinations:

```text
scripts/archive/
scripts/download_yahoo_data.py
reports/trade_logs/
```

Do not rewrite the backtest engine yet. That should be a separate correctness refactor.
