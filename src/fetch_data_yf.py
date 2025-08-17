import yfinance as yf      # Yahoo Finance API wrapper for Python
import pandas as pd        # Data analysis library (tables, time series)
from pathlib import Path   # Safer file/folder handling

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
        auto_adjust=False,   # keep both Close + Adj Close (raw vs adjusted prices)
        progress=False       # disable progress bar for cleaner output
    )

    # Handle empty results early (bad ticker, wrong date range, etc.)
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    # If Yahoo returns MultiIndex columns (rare), flatten them
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Convert index (Date/Datetime) into a normal column
    df = df.reset_index()

    # Figure out if first column is called "Date" or "Datetime"
    date_col = "Date" if "Date" in df.columns else ("Datetime" if "Datetime" in df.columns else df.columns[0])

    # Rename columns into standard OHLCV schema
    rename_map = {
        date_col: "timestamp",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    }
    df = df.rename(columns=rename_map)

    # Prefer "Adj Close" (adjusted close) if it exists → accounts for splits/dividends
    if "Adj Close" in df.columns:
        df["close"] = df["Adj Close"]

    # Convert timestamp to UTC, clean errors
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    # Keep only the standardized columns, sorted by time
    df = df[["timestamp", "open", "high", "low", "close", "volume"]].sort_values("timestamp")

    # Make sure volume is numeric, fill errors with 0
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0)

    # Drop rows where prices or timestamps are missing
    df = df.dropna(subset=["timestamp", "open", "high", "low", "close"])

    return df

def validate_and_preview(df: pd.DataFrame, ticker: str) -> bool:
    """Quick checks + preview for sanity (prints first/last rows + stats)."""
    if df.empty:
        print(f"⚠️ No data fetched for {ticker}. Check ticker/dates/interval.")
        return False
    
    # Show quick preview + summary stats
    print(f"\n✅ Data preview for {ticker}:")
    print(df.head(3))  # first 3 rows
    print("...")
    print(df.tail(3))  # last 3 rows
    print(f"\nRows: {len(df)} | Range: {df['timestamp'].min().date()} → {df['timestamp'].max().date()}")
    print(f"Price range: {df['close'].min():.2f} → {df['close'].max():.2f}")
    return True

if __name__ == "__main__":
    # Ask user for ticker + dates + interval interactively
    symbol = input("Enter ticker (e.g., AAPL, SPY, BTC-USD): ").strip()
    start  = input("Enter start date (YYYY-MM-DD): ").strip()
    end    = input("Enter end date (YYYY-MM-DD): ").strip()
    interval = (input("Enter interval (1d, 1h, 1wk, etc.): ").strip() or "1d")

    # Fetch data
    df = fetch_data_yf(symbol, start, end, interval)

    # Validate + save if non-empty
    if validate_and_preview(df, symbol):
        repo_root = Path(__file__).resolve().parents[1]  # project root folder
        safe_name = symbol.lower().replace("-", "_")     # filename-safe version of ticker
        out_path = repo_root / "data" / "raw" / f"{safe_name}_{interval}_{start}_{end}_yf.csv"
        out_path.parent.mkdir(parents=True, exist_ok=True)  # make folder if missing
        df.to_csv(out_path, index=False)  # save CSV without index column
        print(f"\n💾 Saved {out_path} ({len(df)} rows)")