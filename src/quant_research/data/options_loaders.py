"""Yahoo Finance option chain loaders (no UI dependencies)."""

from __future__ import annotations

import yfinance as yf


def fetch_option_expirations(symbol: str) -> list[str]:
    """Return listed expiration dates for ``symbol`` (YYYY-MM-DD strings)."""
    return list(yf.Ticker(symbol).options)


def fetch_option_chain(symbol: str, expiration: str) -> tuple:
    """
    Fetch call and put chains for one expiration.

    Returns:
        (calls_df, puts_df) as copies safe to mutate.
    """
    chain = yf.Ticker(symbol).option_chain(expiration)
    return chain.calls.copy(), chain.puts.copy()


def fetch_option_chains(symbol: str, expirations: list[str]) -> dict[str, tuple]:
    """
    Fetch multiple expirations in one session (one Ticker instance).

    Missing or failed expirations are skipped; returned dict may be partial.
    """
    if not expirations:
        return {}

    ticker = yf.Ticker(symbol)
    chains: dict[str, tuple] = {}
    for expiration in expirations:
        try:
            chain = ticker.option_chain(expiration)
            chains[expiration] = (chain.calls.copy(), chain.puts.copy())
        except Exception:
            continue
    return chains
