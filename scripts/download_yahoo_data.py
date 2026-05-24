"""Download normalized Yahoo Finance OHLCV data into data/raw/.

Run from the repository root:

    python scripts/download_yahoo_data.py
"""

from pathlib import Path

import pandas as pd

from src.quant_research.data.loaders import fetch_yahoo_history


def fetch_data_yf(ticker: str, start_date: str, end_date: str, interval: str = "1d") -> pd.DataFrame:
    """Fetch normalized Yahoo Finance data."""
    return fetch_yahoo_history(ticker, interval, start_date, end_date)


def validate_and_preview(df: pd.DataFrame, ticker: str) -> bool:
    """Print quick sanity checks before saving."""
    if df.empty:
        print(f"No data fetched for {ticker}. Check ticker/dates/interval.")
        return False

    print(f"\nData preview for {ticker}:")
    print(df.head(3))
    print("...")
    print(df.tail(3))
    print(f"\nRows: {len(df)} | Range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
    print(f"Price range: {df['close'].min():.2f} to {df['close'].max():.2f}")
    return True


def main():
    """Prompt for download inputs and save a normalized CSV."""
    symbol = input("Enter ticker (e.g., AAPL, SPY, BTC-USD): ").strip()
    start = input("Enter start date (YYYY-MM-DD): ").strip()
    end = input("Enter end date (YYYY-MM-DD): ").strip()
    interval = input("Enter interval (1d, 1h, 1wk, etc.): ").strip() or "1d"

    df = fetch_data_yf(symbol, start, end, interval)

    if validate_and_preview(df, symbol):
        repo_root = Path(__file__).resolve().parents[1]
        safe_name = symbol.lower().replace("-", "_")
        out_path = repo_root / "data" / "raw" / f"{safe_name}_{interval}_{start}_{end}_yf.csv"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
        print(f"\nSaved {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    main()
