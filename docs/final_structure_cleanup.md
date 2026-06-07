# Final Structure Cleanup

## Scope

This cleanup removed the temporary compatibility wrappers and archived legacy artifacts after the `src/quant_research/` package became the final active structure.

## Removed

Removed old wrapper packages:

- `src/data/`
- `src/indicators/`
- `src/sentiment/`
- `src/strategies/`
- `src/ui/`
- `src/utils/`
- `src/visualization/`

Removed archived artifacts:

- `scripts/archive/`
- `archive/misc/`
- `notebooks/archive/`

Removed the legacy import-path test from `tests/test_backtests.py`.

## Final Active Structure

```text
app.py
scripts/
  download_yahoo_data.py
src/
  quant_research/
    apps/
      streamlit/
        components/
        pages/
        services/
        state/
        main.py
        router.py
    backtesting/
      engine.py
      runners.py
    config/
    data/
    indicators/
    metrics/
    sentiment/
    strategies/
    utils/
    visualization/
tests/
data/
reports/
docs/
notebooks/
```

## Current Entrypoints

Run the app:

```bash
streamlit run app.py
```

Download Yahoo Finance data:

```bash
python scripts/download_yahoo_data.py
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Validation

Run from the repository root:

```bash
python3 -m compileall -q app.py src scripts tests
.venv/bin/python -m unittest discover -s tests
.venv/bin/python -c "import app; print('app import ok')"
.venv/bin/python -c "from src.quant_research.apps.streamlit.main import main; print('streamlit app import ok')"
.venv/bin/python -c "from scripts.download_yahoo_data import fetch_data_yf; print('download script import ok')"
```

## Notes

The intermediate refactor handoff docs are historical. This file and `README.md` describe the final active structure.
