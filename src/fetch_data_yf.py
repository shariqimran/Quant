import yfinance as yf
import pandas as pd
from pathlib import Path

def fetch_data_yf(ticker: str, start_date: str, end_date: str, interval: str = '1d') -> pd.DataFrame:
    """
    Fetch OHLCV data from Yahoo Finance for a specific date range.

    Args:
        ticker (str): Ticker symbol (e.g., "AAPL", "SPY", "BTC-USD").
        start_date (str): Start date in "YYYY-MM-DD".
        end_date (str): End date in "YYYY-MM-DD".
        interval (str): Data frequency ("1d", "1h", "1wk", etc.).

    Returns:
        pd.DataFrame: DataFrame with standardized columns.
    """
    df = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval=interval,
        auto_adjust=False,   # so 'Adj Close' is present and 'Close' is raw
        progress=False
    )

    # Handle empty results early
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    # If yfinance ever returns a MultiIndex on columns, flatten/select first level
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Make index a column (name may be 'Date' or 'Datetime' depending on interval)
    df = df.reset_index()

    # Find the actual datetime column name
    date_col = "Date" if "Date" in df.columns else ("Datetime" if "Datetime" in df.columns else df.columns[0])

    # Standardize column names
    rename_map = {
        date_col: "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    }
    df = df.rename(columns=rename_map)

    # Some tickers (equities) also have 'Adj Close'—we’ll prefer adjusted if available
    if "Adj Close" in df.columns:
        df["close"] = df["Adj Close"]

    # Types, sort, and clean
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df = df[["timestamp", "open", "high", "low", "close", "volume"]].sort_values("timestamp")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)
    df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])

    return df

def validate_and_preview(df: pd.DataFrame, ticker: str) -> bool:
    """Quick checks + preview for sanity."""
    if df.empty:
        print(f"⚠️ No data fetched for {ticker}. Check ticker/dates/interval.")
        return False
    
    # Basic stats
    print(f"\n✅ Data preview for {ticker}:")
    print(df.head(3))
    print("...")
    print(df.tail(3))
    print(f"\nRows: {len(df)} | Range: {df['timestamp'].min().date()} → {df['timestamp'].max().date()}")
    print(f"Price range: {df['close'].min():.2f} → {df['close'].max():.2f}")
    return True

if __name__ == "__main__":
    symbol = input("Enter ticker (e.g., AAPL, SPY, BTC-USD): ").strip()
    start  = input("Enter start date (YYYY-MM-DD): ").strip()
    end    = input("Enter end date (YYYY-MM-DD): ").strip()
    interval = (input("Enter interval (1d, 1h, 1wk, etc.): ").strip() or "1d")

    df = fetch_data_yf(symbol, start, end, interval)

    if validate_and_preview(df, symbol):
        repo_root = Path(__file__).resolve().parents[1]
        safe_name = symbol.lower().replace("-", "_")
        out_path = repo_root / "data" / "raw" / f"{safe_name}_{interval}_yf.csv"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
        print(f"\n💾 Saved {out_path} ({len(df)} rows)")