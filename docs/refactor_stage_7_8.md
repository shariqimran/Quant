# Refactor Stage 7-8 Handoff

## Scope

This stage focused on test coverage and documentation after the source/package cleanup.

The goal was to make the repository safer to change before touching the higher-risk backtest architecture.

## Stage 7: Tests Added

Added:

- `tests/test_data_validation.py`
- `tests/test_backtests.py`

Expanded test coverage now includes:

- required-column validation,
- empty DataFrame rejection,
- duplicate timestamp detection,
- moving-average backtest trade behavior,
- RSI backtest trade behavior,
- existing indicator, metric, and date-helper checks.

## Why The Backtest Tests Matter

`src/strategies/backtest.py` is still an older mixed-responsibility module. It contains:

- strategy execution,
- trade log creation,
- Plotly chart creation,
- Streamlit error reporting.

Before splitting that file, we need behavior tests so we can tell whether a refactor changed the outputs.

The new tests use tiny deterministic datasets:

- MA test: verifies a golden cross creates a BUY and a death cross creates a SELL.
- RSI test: verifies an oversold RSI creates a BUY and an overbought RSI creates a SELL.

These are behavior-locking tests. They do not claim the strategy methodology is fully realistic yet.

## Stage 8: Documentation Updated

Updated `README.md` with:

- current test command,
- what the test suite covers,
- known quant limitations,
- development notes for where code/artifacts should live.

## Validation Results

Commands run from the repository root:

```bash
python3 -m compileall -q app.py src scripts tests
.venv/bin/python -m unittest discover -s tests
```

Result:

```text
Ran 11 tests
OK
```

## Current Test Suite

```text
tests/
├── test_backtests.py
├── test_data_validation.py
├── test_indicators.py
├── test_metrics.py
└── test_utils.py
```

## Remaining Risks

The largest remaining technical risk is still the active backtest module:

```text
src/strategies/backtest.py
```

It should eventually be split into:

- pure backtest engine,
- strategy signal logic,
- trade log helpers,
- chart builders,
- Streamlit wrapper/UI calls.

That should be done in a separate pass because it changes a high-value part of the project.

## Recommended Next Stage

Refactor backtesting in a behavior-preserving way:

1. Create pure modules under `src/quant_research/backtesting/` and `src/quant_research/visualization/`.
2. Move chart creation out of strategy execution.
3. Remove direct `streamlit` imports from backtest logic.
4. Keep `src/strategies/backtest.py` as a compatibility wrapper temporarily.
5. Run the 11-test suite after each small move.

This unlocks cleaner future work on transaction costs, next-bar execution, drawdown metrics, and buy-and-hold benchmarks.
