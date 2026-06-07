# Code Review Handoff

This document is a practical handoff for someone starting fresh in this repository. It explains what the repo appears to do, which files matter most, what is likely legacy code, and what should be fixed before trusting the app or backtest results.

## Executive Summary

This is a Python/Streamlit quantitative trading analysis project. The main user-facing application is `app.py`. It fetches market data from Yahoo Finance, calculates technical indicators, renders Plotly charts, runs simple backtests, and has an experimental sentiment tab.

The current app path is reasonably organized under `src/`, but the repository also contains older standalone scripts and notebooks. Those older scripts overlap conceptually with the app but do not always use the same data fetching, strategy rules, or file paths.

The biggest technical issue is not syntax or installation. The bigger issue is correctness and maintainability: the backtests have lookahead bias, the portfolio charts are incomplete, some legacy scripts depend on missing packages, and the code mixes app UI concerns with strategy logic.

## How To Run

From the repo root:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

If using the provided script:

```bash
./run_app.sh
```

`run_app.sh` activates `.venv` if it exists, then runs `streamlit run app.py`.

## Project Map

### Current App Path

These are the files that matter for the Streamlit application:

- `app.py`: main Streamlit entry point.
- `src/ui/components.py`: sidebar controls, tab UI, and page text.
- `src/data/data_fetcher.py`: Yahoo Finance fetch logic and return calculation.
- `src/indicators/technical_indicators.py`: moving averages, volatility, RSI, return stats.
- `src/strategies/backtest.py`: moving average and RSI backtest logic plus backtest charts.
- `src/visualization/charts.py`: Plotly volatility and indicator charts.
- `src/sentiment/sentiment_analyzer.py`: experimental Reddit and Google News RSS sentiment.
- `src/utils/helpers.py`: date filtering, formatting helpers, periods-per-year utility.

### Legacy Or Experimental Files

These files appear to be older learning scripts or experiments:

- `src/fetch_data.py`: Binance/CCXT data fetcher for BTC/USDT.
- `src/fetch_data_yf.py`: interactive Yahoo Finance fetcher that saves CSVs.
- `src/backtest.py`: older standalone moving average script using matplotlib.
- `src/rsi.py`: older standalone RSI script using matplotlib and a different strategy rule.
- `src/movingAverage.py`: older moving average backtest function.
- `notebooks/`: exploratory notebooks.
- `Untitled.ipynb`: root-level notebook.
- `src/trade_log.csv` and `src/trade_log_rsi.csv`: generated outputs from older scripts.

Treat `app.py` and the modular folders under `src/` as the current system. Treat the standalone scripts directly under `src/` as legacy unless intentionally revived.

## Data Flow

The main app flow is:

1. `app.py` calls `render_sidebar_inputs()` from `src/ui/components.py`.
2. User enters a ticker, interval, start date, and end date.
3. On "Fetch & Analyze Data", `app.py` calls `fetch_data()` from `src/data/data_fetcher.py`.
4. `fetch_data()` uses `yfinance.Ticker(symbol).history(...)`.
5. The fetched data is normalized to this schema:

```text
timestamp, open, high, low, close, volume
```

6. `calculate_returns()` adds:

```text
return_arith, return_log
```

7. Tabs in `app.py` run volatility analysis, RSI backtest, moving average backtest, sentiment analysis, summary stats, and CSV export.

## Review Findings

### High Priority

#### 1. Backtests Have Lookahead Bias

File:

- `src/strategies/backtest.py`

The moving average strategy calculates whether a crossover happened using the current row's close and then buys or sells at that same current row's close. The RSI strategy has the same issue: it reads the current row's RSI and trades at that same row's close.

Why this matters:

In real trading, you only know the close-derived signal after the candle closes. If you trade at the same close, the backtest uses information that would not have been available at execution time. This makes results too optimistic.

Recommended fix:

- Generate signals using completed bars.
- Execute trades on the next bar's open, or next bar's close if open is unavailable.
- Make execution timing explicit in the UI and docs.

#### 2. Portfolio Charts Are Not Full Equity Curves

File:

- `src/strategies/backtest.py`

The portfolio value trace is plotted only at trade dates. If there are no trades, the chart can be mostly empty. If there are few trades, the chart does not show portfolio movement between trades. It also does not clearly mark final mark-to-market value when a position remains open.

Why this matters:

Users may think they are seeing a real equity curve, but they are only seeing trade-event portfolio values.

Recommended fix:

- Track cash, shares, position, and total equity for every row.
- Plot equity over the full date range.
- Include buy-and-hold comparison.
- Include final unrealized position value.

#### 3. Legacy Binance Script Has A Missing Dependency

File:

- `src/fetch_data.py`

This file imports `ccxt`, but `ccxt` is not listed in `requirements.txt`.

Why this matters:

The Streamlit app does not use this file, so the app can run without `ccxt`. But anyone trying to run the legacy Binance fetcher will hit `ModuleNotFoundError: No module named 'ccxt'`.

Recommended fix:

- If keeping `src/fetch_data.py`, add `ccxt` to requirements.
- If not keeping it, move it to `archive/` or delete it.
- Add a note in README explaining the supported data source.

#### 4. Legacy Scripts Use Fragile Relative Paths

Files:

- `src/fetch_data.py`
- `src/backtest.py`
- `src/rsi.py`

These files use paths like `../data/btc_usdt.csv`. Those paths are relative to the current shell working directory, not the script's location.

Why this matters:

Running a script from the repo root versus from inside `src/` changes what `../data/...` means. This can fail or write files outside the repo.

Recommended fix:

Use `Path(__file__).resolve()` to build paths relative to the repository root.

Example pattern:

```python
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "btc_usdt.csv"
```

### Medium Priority

#### 5. Date Filtering Excludes Most Intraday End-Date Data

File:

- `src/utils/helpers.py`

`filter_df_utc_date_range()` converts the selected end date to midnight UTC and applies `timestamp <= end_dt`.

Why this matters:

For intraday data, choosing an end date like `2026-05-23` will include only `2026-05-23 00:00:00 UTC`, excluding the rest of that date.

Recommended fix:

For date-only inputs, convert the end date to the exclusive start of the next day:

```python
mask = (timestamp >= start_dt) & (timestamp < end_dt + pd.Timedelta(days=1))
```

Alternatively, normalize all filtering around date-only comparisons if the UI is date-based.

#### 6. Strategy Logic Is Coupled To Streamlit

File:

- `src/strategies/backtest.py`

The strategy module imports Streamlit and calls `st.error()` inside backtest functions.

Why this matters:

Backtest logic should be testable without Streamlit. UI rendering and business logic should be separated.

Recommended fix:

- Make backtest functions pure Python functions.
- Return structured errors or raise exceptions.
- Let `app.py` decide how to display those errors.

#### 7. Moving Average UI Allows Invalid Window Relationships

File:

- `src/ui/components.py`

The UI lets users choose a short moving average up to 50 and a long moving average as low as 20. That means users can pick a "short" window that is longer than the "long" window.

Why this matters:

The labels become misleading and the strategy interpretation becomes confusing.

Recommended fix:

- Enforce `short_window < long_window`.
- Either dynamically set the long-window minimum or show a validation error before running.

#### 8. Sentiment Analysis Is Experimental

File:

- `src/sentiment/sentiment_analyzer.py`

The sentiment module fetches Reddit RSS and Google News RSS, scores text with VADER, and returns a simple verdict.

Current limitations:

- No request timeout.
- No source deduplication.
- No recency weighting.
- No robust ticker disambiguation.
- Google News is hardcoded to Canada locale.
- Reddit RSS fetching may be blocked or rate-limited.
- The output looks more confident than the method supports.

Recommended fix:

- Label the tab as experimental.
- Add timeout/error handling.
- Deduplicate links and titles.
- Add recency weighting.
- Make locale configurable.
- Avoid presenting "Favorable" or "Avoid" as trading advice.

#### 9. Volatility Annualization Is Too Simplistic For Intraday Data

Files:

- `src/indicators/technical_indicators.py`
- `src/utils/helpers.py`

The periods-per-year mapping assumes crypto-like 24/7 trading for intraday intervals:

```text
1h = 24 * 365
```

Why this matters:

That can be reasonable for crypto, but it is wrong for equities, which trade only during market hours. AAPL 1h volatility should not be annualized like BTC 1h volatility.

Recommended fix:

- Add an asset-market assumption: crypto 24/7 versus equities.
- Or show volatility as per-period unless annualization assumptions are explicit.

### Low Priority

#### 10. README Is Partially Stale

File:

- `README.md`

Examples:

- It references a `trade_logs/` directory, but generated logs currently exist under `src/`.
- It mentions "Price & Moving Averages" as a tab, but the app currently has volatility, RSI, MA backtest, sentiment, summary, and export tabs.

Recommended fix:

Update README after deciding which files are current and which are archived.

#### 11. Generated And Local Files Should Be Cleaned Up

Observed files:

- `src/trade_log.csv`
- `src/trade_log_rsi.csv`
- `googlea0953003ef3c7c99.html`
- `.DS_Store`
- `.idea/`
- root file named `...`

Recommended fix:

- Decide which generated artifacts belong in git.
- Ignore local editor files if not intentionally tracked.
- Remove accidental empty files like `...` after confirming they are not needed.

## Suggested Cleanup Plan

### Phase 1: Make The Repo Understandable

Goal: separate active app code from historical experiments.

Tasks:

1. Create `archive/` or `legacy/`.
2. Move old scripts there:
   - `src/fetch_data.py`
   - `src/backtest.py`
   - `src/rsi.py`
   - `src/movingAverage.py`
3. Move generated trade logs out of `src/`.
4. Update README with the current project map.
5. Delete accidental empty file `...` if confirmed unnecessary.

### Phase 2: Fix Backtest Correctness

Goal: make results less misleading.

Tasks:

1. Refactor backtest functions out of Streamlit.
2. Add next-bar execution.
3. Track equity on every timestamp.
4. Add buy-and-hold benchmark.
5. Validate inputs:
   - non-empty data
   - enough rows for indicator windows
   - short window less than long window
   - positive prices
6. Add tests for simple deterministic price series.

### Phase 3: Improve App Reliability

Goal: reduce confusing app failures.

Tasks:

1. Fix date filtering for intraday data.
2. Add clearer error messages when Yahoo returns no data.
3. Add a dedicated price and moving average chart tab, or remove it from README.
4. Make annualization assumptions explicit.
5. Cache sentiment results or make sentiment clearly optional.

### Phase 4: Add Tests And Tooling

Goal: prevent regressions.

Recommended minimal tests:

- `calculate_returns()` produces expected arithmetic and log returns.
- `calculate_moving_averages()` produces expected rolling averages.
- `calculate_rsi()` handles rising, falling, and flat series.
- Moving average backtest trades on next bar.
- RSI backtest trades on next bar.
- Date filtering includes the full selected end date for intraday data.

Recommended tooling:

- `pytest`
- `ruff`
- optional: `mypy` after code is cleaner

## Suggested Future Structure

One possible cleaned-up layout:

```text
.
├── app.py
├── README.md
├── requirements.txt
├── CODE_REVIEW_HANDOFF.md
├── data/
│   └── raw/
├── notebooks/
├── src/
│   ├── data/
│   ├── indicators/
│   ├── strategies/
│   ├── sentiment/
│   ├── ui/
│   ├── utils/
│   └── visualization/
├── tests/
└── archive/
    └── legacy_scripts/
```

## Current Status From Review

What passed:

- Python syntax compile passed for `app.py` and `src/`.
- Main app dependencies imported successfully in the local `.venv`.
- Basic synthetic-data smoke calls for indicators and backtests returned values.

What failed or is missing:

- `ccxt` is not installed, so `src/fetch_data.py` cannot run as-is.
- No test suite was found.
- `rg` is not installed in the shell environment, so file searching used `find`.

## Key Takeaway

The Streamlit app is the real product in this repo. The current code can be run and explored, but the backtest results should not be trusted for decision-making until the execution timing, equity curve, input validation, and tests are fixed.
