# Architecture Refactor Plan

This document is an inspection-only architecture plan for restructuring the quant research repository into a cleaner, more professional, maintainable project.

Initial inspection was performed before edits. Implementation handoffs now live in:

- `docs/refactor_stage_1_2.md`
- `docs/refactor_stage_3_4.md`
- `docs/refactor_stage_5_6.md`
- `docs/refactor_stage_7_8.md`
- `docs/refactor_stage_9.md`
- `docs/final_structure_cleanup.md`

## Goals

- Clear organization
- Easy navigation
- Separation of concerns
- Testability
- Maintainability
- Scalability
- Professional portfolio polish
- Easy onboarding for another developer

## Current Repository Summary

Current structure:

```text
.
├── app.py
├── README.md
├── CODE_REVIEW_HANDOFF.md
├── requirements.txt
├── run_app.sh
├── data/
│   ├── btc_usdt.csv
│   └── raw/
│       ├── aapl_1d_2010-01-01_2025-08-16_yf.csv
│       └── spy_1d_2020-01-01_2025-08-16_yf.csv
├── notebooks/
│   ├── backtest.ipynb
│   ├── dataviz.ipynb
│   └── explore_data_yf.ipynb
├── src/
│   ├── data/data_fetcher.py
│   ├── indicators/technical_indicators.py
│   ├── strategies/backtest.py
│   ├── visualization/charts.py
│   ├── sentiment/sentiment_analyzer.py
│   ├── ui/components.py
│   ├── utils/helpers.py
│   ├── fetch_data.py
│   ├── fetch_data_yf.py
│   ├── backtest.py
│   ├── rsi.py
│   ├── movingAverage.py
│   ├── trade_log.csv
│   └── trade_log_rsi.csv
└── misc files:
    ├── Untitled.ipynb
    ├── googlea0953003ef3c7c99.html
    ├── ...
    ├── .DS_Store
    └── .devcontainer/
```

## Main File Roles

| File | Current role |
|---|---|
| `app.py` | Streamlit app entrypoint, router, page rendering, data loading, strategy execution, metrics display |
| `src/ui/components.py` | CSS, sidebar, forms, home page, KPI cards, mini chart, empty states, strategy UI |
| `src/data/data_fetcher.py` | Active Yahoo Finance data loader and return calculation |
| `src/indicators/technical_indicators.py` | Moving averages, volatility, RSI, return stats |
| `src/strategies/backtest.py` | Active MA/RSI backtest logic plus Plotly backtest charts |
| `src/visualization/charts.py` | Volatility and indicator charts |
| `src/sentiment/sentiment_analyzer.py` | Experimental Reddit/Google News RSS sentiment |
| `src/backtest.py` | Legacy standalone moving average script |
| `src/rsi.py` | Legacy standalone RSI script |
| `src/movingAverage.py` | Legacy moving average helper/backtest |
| `src/fetch_data.py` | Legacy Binance/CCXT data fetch script |
| `src/fetch_data_yf.py` | Interactive Yahoo Finance data download script |
| `notebooks/` | Exploratory notebooks |
| `data/` | Sample/static datasets |
| `src/trade_log*.csv` | Generated outputs currently stored inside source tree |

## Architecture Problems

### 1. `app.py` Is Too Large

`app.py` currently owns too many responsibilities:

- app lifecycle
- page routing
- data loading
- market data page
- volatility page
- strategy page
- risk metrics page
- sentiment page
- export page
- backtest execution

The root entrypoint should be thin and should delegate to an application package.

### 2. `src/ui/components.py` Is A Catch-All UI File

`src/ui/components.py` is currently large and mixed-purpose. It contains:

- global CSS
- page config
- header
- sidebar
- home page
- KPI card rendering
- mini chart
- empty states
- strategy parameter forms
- sentiment UI

This should be split into page modules and reusable UI components.

### 3. No Real Package Name

Imports currently look like:

```python
from src.data.data_fetcher import fetch_data
```

This works locally, but a professional package layout should use a real package name:

```python
from quant_research.data.loaders import fetch_market_data
```

Recommended package root:

```text
src/quant_research/
```

### 4. Domain Logic Is Mixed With UI Behavior

Examples:

- `app.py` controls backtest execution details.
- `src/strategies/backtest.py` imports Streamlit and calls `st.error`.
- UI forms and quant parameter validation are mixed in `src/ui/components.py`.

Backtesting and indicator logic should be testable without Streamlit.

### 5. Active Code And Legacy Scripts Are Mixed

Legacy/experimental files are currently inside `src/` alongside active modules:

```text
src/backtest.py
src/rsi.py
src/movingAverage.py
src/fetch_data.py
```

These should move to `scripts/archive/` unless we intentionally revive them.

### 6. Generated Outputs Live Inside Source

These files should not live in `src/`:

```text
src/trade_log.csv
src/trade_log_rsi.csv
```

Generated outputs belong under `reports/`, `outputs/`, or `archive/`.

### 7. No Test Suite

There is no `tests/` directory.

Core logic that should be tested:

- return calculation
- moving averages
- RSI
- volatility
- date filtering
- performance metrics
- data validation

### 8. Fragile Path Handling In Legacy Scripts

Legacy scripts use relative paths like:

```python
../data/btc_usdt.csv
```

These depend on the current working directory and should be replaced with centralized path helpers.

### 9. No Config Or Path Layer

Defaults are currently scattered:

- date ranges
- intervals
- volatility windows
- backtest defaults
- data paths

A small config module would improve maintainability.

### 10. Notebook Boundaries Are Unclear

`Untitled.ipynb` is in the repo root while other notebooks live under `notebooks/`.

Reusable logic should live under `src/quant_research/`, and notebooks should import from the package.

## Recommended Target Structure

Recommended long-term structure:

```text
.
├── app.py
├── README.md
├── requirements.txt
├── pyproject.toml
├── run_app.sh
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── architecture_refactor_plan.md
│   ├── review_handoff.md
│   └── roadmap.md
├── notebooks/
│   ├── backtest.ipynb
│   ├── dataviz.ipynb
│   ├── explore_data_yf.ipynb
│   └── archive/
├── reports/
│   └── trade_logs/
├── scripts/
│   ├── download_yahoo_data.py
│   └── archive/
├── src/
│   └── quant_research/
│       ├── __init__.py
│       ├── apps/
│       │   └── streamlit/
│       │       ├── __init__.py
│       │       ├── main.py
│       │       ├── router.py
│       │       ├── pages/
│       │       │   ├── __init__.py
│       │       │   ├── home.py
│       │       │   ├── market_data.py
│       │       │   ├── strategy_lab.py
│       │       │   ├── risk_metrics.py
│       │       │   ├── sentiment.py
│       │       │   └── export.py
│       │       ├── components/
│       │       │   ├── __init__.py
│       │       │   ├── sidebar.py
│       │       │   ├── layout.py
│       │       │   ├── cards.py
│       │       │   ├── forms.py
│       │       │   └── styles.py
│       │       └── state/
│       │           ├── __init__.py
│       │           └── session.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py
│       │   └── paths.py
│       ├── data/
│       │   ├── __init__.py
│       │   ├── loaders.py
│       │   ├── schemas.py
│       │   └── validation.py
│       ├── indicators/
│       │   ├── __init__.py
│       │   ├── momentum.py
│       │   ├── trend.py
│       │   └── volatility.py
│       ├── strategies/
│       │   ├── __init__.py
│       │   ├── moving_average.py
│       │   └── rsi.py
│       ├── backtesting/
│       │   ├── __init__.py
│       │   ├── engine.py
│       │   └── trades.py
│       ├── metrics/
│       │   ├── __init__.py
│       │   ├── performance.py
│       │   └── risk.py
│       ├── visualization/
│       │   ├── __init__.py
│       │   ├── market_charts.py
│       │   ├── backtest_charts.py
│       │   └── volatility_charts.py
│       ├── sentiment/
│       │   ├── __init__.py
│       │   └── analyzer.py
│       └── utils/
│           ├── __init__.py
│           ├── dates.py
│           └── formatting.py
└── tests/
    ├── test_data_validation.py
    ├── test_indicators.py
    ├── test_metrics.py
    └── test_date_filters.py
```

Root `app.py` should remain as a backwards-compatible entrypoint:

```python
from quant_research.apps.streamlit.main import main

if __name__ == "__main__":
    main()
```

## File Migration Map

| Current file/folder | Proposed location | Reason | Risk |
|---|---|---|---|
| `app.py` | keep as thin root entrypoint | Preserve `streamlit run app.py`; move logic elsewhere | Medium |
| `src/ui/components.py` | split into `apps/streamlit/components/*.py` and `apps/streamlit/pages/home.py` | Separate CSS, sidebar, forms, cards, pages | Medium |
| `src/data/data_fetcher.py` | `src/quant_research/data/loaders.py` | Active data loading logic | Low |
| `src/indicators/technical_indicators.py` | split into `indicators/trend.py`, `indicators/momentum.py`, `indicators/volatility.py`, `metrics/performance.py` | Separate indicators from metrics | Medium |
| `src/strategies/backtest.py` | split into `backtesting/engine.py`, `visualization/backtest_charts.py`, `strategies/*.py` | Remove Streamlit coupling and separate logic/charts | High |
| `src/visualization/charts.py` | `visualization/volatility_charts.py`, `visualization/market_charts.py` | Chart builders only | Low |
| `src/utils/helpers.py` | `utils/dates.py`, `utils/formatting.py`, `config/settings.py` | Avoid vague helper module | Low |
| `src/sentiment/sentiment_analyzer.py` | `sentiment/analyzer.py` | Keep experimental service isolated | Low |
| `src/fetch_data_yf.py` | `scripts/download_yahoo_data.py` | Operational script imports package loader | Low |
| `src/fetch_data.py` | `scripts/archive/fetch_binance_ccxt.py` | Legacy Binance/CCXT script; missing dependency | Medium |
| `src/backtest.py` | `scripts/archive/legacy_ma_backtest_matplotlib.py` | Legacy standalone script | Low |
| `src/rsi.py` | `scripts/archive/legacy_rsi_strategy.py` | Legacy standalone script | Low |
| `src/movingAverage.py` | `scripts/archive/legacy_moving_average.py` | Legacy duplicate naming/style | Low |
| `src/trade_log.csv` | `reports/trade_logs/trade_log.csv` or `archive/generated/` | Generated output should not live in source | Low |
| `src/trade_log_rsi.csv` | `reports/trade_logs/trade_log_rsi.csv` or `archive/generated/` | Generated output should not live in source | Low |
| `CODE_REVIEW_HANDOFF.md` | `docs/review_handoff.md` | Documentation belongs under docs | Low |
| `Untitled.ipynb` | `notebooks/archive/untitled.ipynb` | Root notebook is unclear | Low |
| `notebooks/*.ipynb` | keep under `notebooks/` | Exploratory work belongs there | Low |
| `data/btc_usdt.csv` | keep or move to `data/raw/` | Data organization consistency | Low |
| `googlea0953003ef3c7c99.html` | `public/` or document why root is required | Likely verification file | Low |
| `...` | remove or `archive/misc/...` after confirmation | Appears accidental empty file | Low |
| `.DS_Store` files | remove and ignore | OS artifacts | Low |
| `.idea/` | ignore or document team choice | Local IDE config | Low |
| `requirements.txt` | keep initially; optionally add `pyproject.toml` | Minimize dependency disruption | Low |
| `.devcontainer/` | keep | Useful environment config | Low |

## Staged Refactor Plan

### Stage 1: Create Package Skeleton

Create:

```text
src/quant_research/
```

with subpackages:

```text
apps/
config/
data/
indicators/
strategies/
backtesting/
metrics/
visualization/
sentiment/
utils/
```

Keep old modules temporarily until imports are migrated.

### Stage 2: Move Pure Logic First

Move low-risk logic:

- `data_fetcher.py` → `data/loaders.py`
- `helpers.py` → `utils/dates.py`, `utils/formatting.py`
- parts of `technical_indicators.py` → `indicators/`
- return stats → `metrics/performance.py`

Add tests for these modules first.

### Stage 3: Split Streamlit UI

Move page functions from `app.py` into:

```text
apps/streamlit/pages/
```

Page modules:

```text
home.py
market_data.py
strategy_lab.py
risk_metrics.py
sentiment.py
export.py
```

Move reusable UI into:

```text
apps/streamlit/components/
```

Components:

```text
sidebar.py
cards.py
forms.py
layout.py
styles.py
```

### Stage 4: Make `app.py` Thin

Root `app.py` should only delegate to:

```text
src/quant_research/apps/streamlit/main.py
```

### Stage 5: Refactor Backtesting

This is the highest-risk stage and should be done carefully.

Split:

- pure backtest calculations → `backtesting/engine.py`
- trade log helpers → `backtesting/trades.py`
- chart creation → `visualization/backtest_charts.py`
- strategy signal logic → `strategies/moving_average.py`, `strategies/rsi.py`

Remove Streamlit imports from backtesting logic.

### Stage 6: Move Scripts And Archive Legacy

Move standalone scripts to:

```text
scripts/
scripts/archive/
```

Add:

```text
scripts/archive/README.md
```

to explain that archived scripts are historical/experimental.

### Stage 7: Add Tests

Start with:

```text
tests/test_indicators.py
tests/test_metrics.py
tests/test_date_filters.py
tests/test_data_validation.py
```

Initial test targets:

- moving average rolling output
- RSI output shape and NaN handling
- volatility output column
- return stats no crash on small data
- date filtering expected inclusivity
- duplicate timestamp detection if added

### Stage 8: Update Documentation

Update `README.md` with:

- project purpose
- install instructions
- app command
- test command
- project structure
- known quant limitations
- educational disclaimer

Move handoff docs under `docs/`.

### Stage 9: Clean Generated And Local Files

After confirmation:

- remove `.DS_Store`
- remove `__pycache__`
- ignore `.idea/` or keep intentionally
- decide what to do with `...`
- move generated trade logs

## Validation Plan

### Basic Syntax

```bash
python3 -m compileall -q app.py src
```

### App Import

```bash
.venv/bin/python -c "import app; print('app import ok')"
```

### Run Streamlit

```bash
streamlit run app.py
```

or:

```bash
./run_app.sh
```

If port `8501` is occupied:

```bash
streamlit run app.py --server.port 8502
```

### Manual UI Validation

Check:

- sidebar opens and closes
- Home renders without data
- AAPL daily data loads
- Market Data page renders chart/table
- Strategy Lab page renders MA and RSI forms
- Risk & Metrics page renders volatility and metrics
- Sentiment page does not break if network fails
- Export page downloads CSV

### Tests After Adding Pytest

```bash
pytest
```

If pytest is not installed:

```bash
pip install pytest
pytest
```

### Dependency Validation

```bash
pip install -r requirements.txt
.venv/bin/python -c "import streamlit, pandas, numpy, yfinance, plotly"
```

### Git Cleanliness

```bash
git status --short
```

Confirm only intentional changes remain.

## Recommended Approval Scope

For the implementation pass, the safest first migration is:

1. Create `src/quant_research/`.
2. Move/split the Streamlit app into `apps/streamlit/`.
3. Move current active logic modules with import updates.
4. Keep root `app.py` working.
5. Add basic tests for indicators/date helpers.
6. Move legacy scripts to `scripts/archive/`.
7. Update README.

Do **not** fully rewrite the backtest engine in the same pass. That is a separate correctness refactor and should happen after the structure is stable.

## Notes

The current UI work has made `app.py` and `src/ui/components.py` larger. That was acceptable while iterating quickly, but now these files should be split before further feature work.

The backtesting correctness issues identified in the code review still remain. The architecture refactor should preserve behavior first; backtest correctness should be handled in a separate focused refactor.
