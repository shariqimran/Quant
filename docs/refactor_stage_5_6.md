# Refactor Stage 5-6 Handoff

## Scope

This stage cleaned up repository artifacts after the package and Streamlit UI split.

Stage 5 focused on paths, generated files, and legacy scripts. Stage 6 focused on documentation notes and keeping the repo easier to onboard into.

## What Changed

- Moved the active Yahoo Finance download script from `src/fetch_data_yf.py` to `scripts/download_yahoo_data.py`.
- Archived older standalone scripts under `scripts/archive/`.
- Moved generated trade logs from `src/` to `reports/trade_logs/`.
- Moved sample BTC data from `data/btc_usdt.csv` to `data/sample/btc_usdt.csv`.
- Moved `Untitled.ipynb` to `notebooks/archive/untitled.ipynb`.
- Moved the unknown root placeholder file `...` to `archive/misc/...`.
- Removed `.DS_Store` files from the working tree.
- Added `.DS_Store` and `.idea/` to `.gitignore`.
- Updated `README.md` so it describes the current package, app, scripts, reports, and archive layout.

## Why This Is Better

- `src/` is now closer to source code only, instead of mixing source files, generated CSV outputs, and one-off experiments.
- Operational scripts now live under `scripts/`, which is easier for a new developer to find.
- Generated outputs now live under `reports/`, which makes it clear they are artifacts.
- Sample data now has a dedicated folder separate from downloaded research data.
- Historical scripts were preserved instead of deleted, which keeps learning context without letting old files look like current architecture.

## Active Entrypoints

- Streamlit dashboard: `streamlit run app.py`
- Yahoo Finance downloader: `python scripts/download_yahoo_data.py`
- Unit tests: `python -m unittest discover -s tests`

## Notes

- `googlea0953003ef3c7c99.html` remains at the repository root intentionally. It appears to be a Google site verification file and should stay there if deployment still depends on it.
- The archived scripts may need path updates before they can be run again. Treat them as reference material unless they are reviewed.
- The app still uses the existing `src/strategies/backtest.py` module. A later stage can migrate that logic into `src/quant_research/backtesting/` or `src/quant_research/strategies/` after behavior is covered by tests.

## Validation Plan

Run these commands from the repository root:

```bash
python -m compileall -q app.py src scripts tests
python -m unittest discover -s tests
python -c "import app; print('app import ok')"
python -c "from src.quant_research.apps.streamlit.main import main; print('streamlit app import ok')"
streamlit run app.py
```

Then open the local Streamlit URL and verify:

- the home page renders,
- the hamburger/sidebar can be closed and reopened,
- the dashboard navigation still switches pages,
- market data fetching still works for a simple ticker such as `SPY`,
- exported data and trade logs still land outside the active source package.
