# Refactor Stage 1-2 Implementation Notes

This document records the first restructuring pass.

## Scope

Implemented:

1. Stage 1: Create the `src/quant_research/` package skeleton.
2. Stage 2: Move low-risk pure logic into focused package modules.

Not implemented yet:

- Streamlit page split
- root `app.py` thinning
- legacy script archival
- backtest engine rewrite
- README rewrite

## What Changed

### New Package Skeleton

Created:

```text
src/quant_research/
├── apps/
│   └── streamlit/
│       ├── components/
│       ├── pages/
│       └── state/
├── backtesting/
├── config/
├── data/
├── indicators/
├── metrics/
├── sentiment/
├── strategies/
├── utils/
└── visualization/
```

Most app-specific folders are placeholders for the next refactor stage.

### New Config Modules

Created:

```text
src/quant_research/config/settings.py
src/quant_research/config/paths.py
```

`settings.py` centralizes:

- OHLCV schema
- interval-to-periods-per-year mapping
- annualization defaults

`paths.py` centralizes:

- project root
- data directories
- report directories
- trade log output directory

### New Data Modules

Created:

```text
src/quant_research/data/loaders.py
src/quant_research/data/validation.py
src/quant_research/data/schemas.py
```

Moved reusable logic for:

- Yahoo Finance data loading and normalization
- return column creation
- data summaries
- DataFrame validation

### New Indicator Modules

Created:

```text
src/quant_research/indicators/trend.py
src/quant_research/indicators/momentum.py
src/quant_research/indicators/volatility.py
```

Moved reusable logic for:

- moving averages
- moving-average crossover signal slices
- RSI
- RSI signal slices
- rolling volatility
- volatility summary stats

### New Metrics Modules

Created:

```text
src/quant_research/metrics/performance.py
src/quant_research/metrics/risk.py
```

Moved reusable logic for:

- return statistics
- Sharpe ratio helper
- drawdown helper

### New Utility Modules

Created:

```text
src/quant_research/utils/dates.py
src/quant_research/utils/formatting.py
src/quant_research/utils/runtime.py
```

Moved reusable logic for:

- UTC date filtering
- currency and percent formatting
- warning suppression

## Compatibility Wrappers

To avoid breaking the current app, these old modules were preserved as compatibility wrappers:

```text
src/data/data_fetcher.py
src/indicators/technical_indicators.py
src/utils/helpers.py
```

The current Streamlit app still imports from the old locations. Those files now delegate to the new package modules.

This lets us migrate safely in stages.

## Tests Added

Created:

```text
tests/test_indicators.py
tests/test_metrics.py
tests/test_utils.py
```

These use Python's built-in `unittest` module, so no new dependency was required.

Covered:

- moving-average columns and values
- RSI output shape
- volatility output columns
- return statistics keys
- date range filtering

## Validation Commands Run

```bash
python3 -m compileall -q app.py src tests
.venv/bin/python -c "import app; print('app import ok')"
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -c "from src.quant_research.indicators import calculate_rsi; from src.quant_research.data import calculate_returns; from src.quant_research.metrics import get_return_statistics; print('new package imports ok')"
```

Result:

```text
Ran 5 tests
OK
```

## Current Risk

Low.

The current app path was preserved by compatibility wrappers. No Streamlit page routing or backtest behavior was intentionally changed in this stage.

## Next Recommended Stage

Stage 3:

Split the Streamlit UI into:

```text
src/quant_research/apps/streamlit/main.py
src/quant_research/apps/streamlit/pages/
src/quant_research/apps/streamlit/components/
```

Root `app.py` should eventually become a thin entrypoint.
