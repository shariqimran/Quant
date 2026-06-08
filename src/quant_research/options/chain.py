"""Option chain normalization, filtering, ranking, and model comparison."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from math import isfinite
from typing import Literal

import pandas as pd

from src.quant_research.options.pricing import calculate_black_scholes, years_from_days

OptionType = Literal["call", "put"]

# Configurable defaults (spread threshold is a decimal fraction, e.g. 0.15 = 15%).
MAX_BID_ASK_SPREAD_PCT = 0.15
MAX_DISPLAY_CONTRACTS = 10

# Ranking weights (lower composite score = more relevant).
WEIGHT_STRIKE = 0.45
WEIGHT_EXPIRY = 0.25
WEIGHT_SPREAD = 0.20
WEIGHT_LIQUIDITY = 0.10


@dataclass(frozen=True)
class ListedOptionContract:
    """Normalized listed option contract from Yahoo Finance (no model fields)."""

    contract_symbol: str
    option_type: OptionType
    expiration_date: str
    days_to_expiration: int
    strike: float
    bid: float | None
    ask: float | None
    midpoint: float | None
    last_price: float | None
    implied_volatility: float | None
    volume: int | None
    open_interest: int | None
    spread_percentage: float | None


@dataclass(frozen=True)
class OptionContractComparison:
    """Normalized listed contract with Black-Scholes comparison fields."""

    contract_symbol: str
    option_type: OptionType
    expiration_date: str
    days_to_expiration: int
    strike: float
    bid: float | None
    ask: float | None
    midpoint: float | None
    last_price: float | None
    implied_volatility: float | None
    volume: int | None
    open_interest: int | None
    spread_percentage: float | None
    theoretical_price: float | None
    absolute_difference: float | None
    percentage_difference: float | None
    model_edge: float | None
    is_closest_to_model: bool = False
    has_highest_model_edge: bool = False


def _safe_float(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(number):
        return None
    return number


def _safe_int(value) -> int | None:
    number = _safe_float(value)
    if number is None:
        return None
    return int(number)


def days_to_expiration(expiration: str, *, as_of: date | None = None) -> int:
    """Calendar days from ``as_of`` (default today) to ``expiration`` (YYYY-MM-DD)."""
    expiry_date = datetime.strptime(expiration, "%Y-%m-%d").date()
    reference = as_of or date.today()
    return max((expiry_date - reference).days, 0)


def contract_midpoint(bid: float | None, ask: float | None) -> float | None:
    """Bid-ask midpoint; returns None if either side is missing or non-positive."""
    if bid is None or ask is None or bid <= 0 or ask <= 0:
        return None
    return (bid + ask) / 2.0


def spread_percentage(bid: float | None, ask: float | None, midpoint: float | None) -> float | None:
    if bid is None or ask is None or midpoint is None or midpoint <= 0:
        return None
    return (ask - bid) / midpoint


def passes_liquidity_filters(
    bid: float | None,
    ask: float | None,
    midpoint: float | None,
    spread_pct: float | None,
    *,
    max_spread_pct: float = MAX_BID_ASK_SPREAD_PCT,
) -> bool:
    if bid is None or ask is None or bid <= 0 or ask <= 0:
        return False
    if ask < bid:
        return False
    if midpoint is None or midpoint <= 0:
        return False
    if spread_pct is None or spread_pct > max_spread_pct:
        return False
    return True


def _theoretical_price(
    *,
    option_type: OptionType,
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    risk_free_rate: float,
    dividend_yield: float,
) -> float:
    result = calculate_black_scholes(
        spot=spot,
        strike=strike,
        time_to_expiry=time_to_expiry,
        volatility=volatility,
        risk_free_rate=risk_free_rate,
        dividend_yield=dividend_yield,
    )
    return result.call_price if option_type == "call" else result.put_price


def _comparison_metrics(theoretical: float, midpoint: float, ask: float) -> tuple[float, float | None, float]:
    absolute_difference = abs(theoretical - midpoint)
    percentage_difference = absolute_difference / midpoint if midpoint > 0 else None
    model_edge = theoretical - ask
    return absolute_difference, percentage_difference, model_edge


def _rank_score(
    *,
    strike: float,
    target_strike: float,
    spot: float,
    days: int,
    target_days: int,
    volume: int | None,
    open_interest: int | None,
    spread_pct: float | None,
) -> float:
    strike_norm = abs(strike - target_strike) / max(spot, 1e-6)
    expiry_norm = abs(days - target_days) / max(target_days, 1)
    spread_norm = spread_pct if spread_pct is not None else 1.0
    volume_val = max(volume or 0, 0)
    oi_val = max(open_interest or 0, 0)
    liquidity_norm = 1.0 / (1.0 + volume_val + oi_val)
    return (
        WEIGHT_STRIKE * strike_norm
        + WEIGHT_EXPIRY * expiry_norm
        + WEIGHT_SPREAD * spread_norm
        + WEIGHT_LIQUIDITY * liquidity_norm
    )


def normalize_chain_row(
    row: pd.Series,
    *,
    option_type: OptionType,
    expiration_date: str,
    as_of: date | None = None,
) -> dict:
    """Map a Yahoo Finance chain row to normalized scalar fields."""
    bid = _safe_float(row.get("bid"))
    ask = _safe_float(row.get("ask"))
    midpoint = contract_midpoint(bid, ask)
    return {
        "contract_symbol": str(row.get("contractSymbol") or ""),
        "option_type": option_type,
        "expiration_date": expiration_date,
        "days_to_expiration": days_to_expiration(expiration_date, as_of=as_of),
        "strike": _safe_float(row.get("strike")),
        "bid": bid,
        "ask": ask,
        "midpoint": midpoint,
        "last_price": _safe_float(row.get("lastPrice")),
        "implied_volatility": _safe_float(row.get("impliedVolatility")),
        "volume": _safe_int(row.get("volume")),
        "open_interest": _safe_int(row.get("openInterest")),
        "spread_percentage": spread_percentage(bid, ask, midpoint),
    }


def listed_contract_from_row(
    row: pd.Series,
    *,
    option_type: OptionType,
    expiration_date: str,
    as_of: date | None = None,
) -> ListedOptionContract | None:
    """Build a ``ListedOptionContract`` from a Yahoo chain row, or None if strike is invalid."""
    normalized = normalize_chain_row(
        row,
        option_type=option_type,
        expiration_date=expiration_date,
        as_of=as_of,
    )
    strike = normalized["strike"]
    if strike is None or strike <= 0:
        return None
    return ListedOptionContract(
        contract_symbol=normalized["contract_symbol"],
        option_type=option_type,
        expiration_date=expiration_date,
        days_to_expiration=normalized["days_to_expiration"],
        strike=strike,
        bid=normalized["bid"],
        ask=normalized["ask"],
        midpoint=normalized["midpoint"],
        last_price=normalized["last_price"],
        implied_volatility=normalized["implied_volatility"],
        volume=normalized["volume"],
        open_interest=normalized["open_interest"],
        spread_percentage=normalized["spread_percentage"],
    )


def collect_listed_contracts(
    chains_by_expiration: dict[str, tuple[pd.DataFrame, pd.DataFrame]],
    *,
    include_calls: bool = True,
    include_puts: bool = True,
    as_of: date | None = None,
) -> list[ListedOptionContract]:
    """Collect all listed contracts across expirations without liquidity filtering."""
    contracts: list[ListedOptionContract] = []
    for expiration_date, (calls, puts) in sorted(chains_by_expiration.items()):
        if include_calls and calls is not None and not calls.empty:
            for _, row in calls.iterrows():
                contract = listed_contract_from_row(
                    row,
                    option_type="call",
                    expiration_date=expiration_date,
                    as_of=as_of,
                )
                if contract is not None:
                    contracts.append(contract)
        if include_puts and puts is not None and not puts.empty:
            for _, row in puts.iterrows():
                contract = listed_contract_from_row(
                    row,
                    option_type="put",
                    expiration_date=expiration_date,
                    as_of=as_of,
                )
                if contract is not None:
                    contracts.append(contract)

    contracts.sort(
        key=lambda item: (item.expiration_date, item.strike, item.option_type, item.contract_symbol)
    )
    return contracts


def contracts_to_display_dataframe(contracts: list[ListedOptionContract]) -> pd.DataFrame:
    """Convert listed contracts to a display-ready DataFrame (row order matches ``contracts``)."""
    rows = []
    for contract in contracts:
        rows.append(
            {
                "Contract": contract.contract_symbol,
                "Type": contract.option_type.upper(),
                "Expiration": contract.expiration_date,
                "DTE": contract.days_to_expiration,
                "Strike": contract.strike,
                "Bid": contract.bid,
                "Ask": contract.ask,
                "Midpoint": contract.midpoint,
                "Last": contract.last_price,
                "IV": contract.implied_volatility,
                "Volume": contract.volume,
                "Open Int.": contract.open_interest,
                "Spread %": contract.spread_percentage,
            }
        )
    return pd.DataFrame(rows)


def find_contract_by_symbol(
    contracts: list[ListedOptionContract],
    contract_symbol: str,
) -> ListedOptionContract | None:
    for contract in contracts:
        if contract.contract_symbol == contract_symbol:
            return contract
    return None


def normalize_implied_volatility(implied_volatility: float | None) -> float | None:
    """Normalize Yahoo IV to an annualized decimal (e.g. 0.45 = 45%)."""
    iv = _safe_float(implied_volatility)
    if iv is None or iv <= 0:
        return None
    if iv > 3:
        return iv / 100.0
    return iv


def moneyness_label(option_type: OptionType, strike: float, spot: float | None) -> str:
    """Human-readable moneyness vs spot."""
    if spot is None or spot <= 0:
        return "—"
    pct_from_spot = (strike / spot - 1.0) * 100.0
    if abs(pct_from_spot) < 1.5:
        return "ATM"

    if option_type == "call":
        if strike < spot:
            return f"ITM {abs(pct_from_spot):.1f}%"
        return f"OTM {pct_from_spot:.1f}%"

    if strike > spot:
        return f"ITM {pct_from_spot:.1f}%"
    return f"OTM {abs(pct_from_spot):.1f}%"


def liquidity_tier(
    spread_pct: float | None,
    volume: int | None,
    open_interest: int | None,
) -> str:
    """Short liquidity label for table display."""
    if spread_pct is None:
        return "No quote"
    if spread_pct <= 0.05:
        label = "Tight spread"
    elif spread_pct <= MAX_BID_ASK_SPREAD_PCT:
        label = "Tradeable"
    else:
        label = "Wide spread"
    if (volume or 0) + (open_interest or 0) == 0:
        return f"{label} · low activity"
    return label


def summarize_contract_chain(contracts: list[ListedOptionContract], spot: float | None) -> dict:
    """Aggregate stats for the chain table header."""
    if not contracts:
        return {
            "count": 0,
            "quoted": 0,
            "liquid": 0,
            "median_spread_pct": None,
            "atm_strike": None,
        }

    spreads = [contract.spread_percentage for contract in contracts if contract.spread_percentage is not None]
    quoted = sum(1 for contract in contracts if contract.midpoint is not None)
    liquid = sum(
        1
        for contract in contracts
        if contract.spread_percentage is not None and contract.spread_percentage <= MAX_BID_ASK_SPREAD_PCT
    )
    atm_strike = None
    if spot is not None and spot > 0:
        atm_strike = min(contracts, key=lambda contract: abs(contract.strike - spot)).strike

    return {
        "count": len(contracts),
        "quoted": quoted,
        "liquid": liquid,
        "median_spread_pct": float(pd.Series(spreads).median()) if spreads else None,
        "atm_strike": atm_strike,
    }


def build_enriched_contract_table(
    contracts: list[ListedOptionContract],
    *,
    spot: float | None,
) -> pd.DataFrame:
    """Build an interpretable, consistently formatted table DataFrame."""
    rows = []
    for contract in contracts:
        iv_decimal = normalize_implied_volatility(contract.implied_volatility)
        spread_pct = contract.spread_percentage
        rows.append(
            {
                "Strike": contract.strike,
                "Type": contract.option_type.upper(),
                "Moneyness": moneyness_label(contract.option_type, contract.strike, spot),
                "Bid": contract.bid,
                "Ask": contract.ask,
                "Mid": contract.midpoint,
                "IV %": (iv_decimal * 100.0) if iv_decimal is not None else None,
                "Spread %": (spread_pct * 100.0) if spread_pct is not None else None,
                "Volume": contract.volume if contract.volume is not None else 0,
                "Open Int.": contract.open_interest if contract.open_interest is not None else 0,
                "Liquidity": liquidity_tier(spread_pct, contract.volume, contract.open_interest),
                "Contract": contract.contract_symbol,
            }
        )
    return pd.DataFrame(rows)


def filter_and_sort_contracts(
    contracts: list[ListedOptionContract],
    *,
    strike_min: float,
    strike_max: float,
    liquid_only: bool,
    sort_by: str,
    spot: float | None,
) -> list[ListedOptionContract]:
    """Apply UI filters while preserving ``ListedOptionContract`` objects."""
    filtered = [contract for contract in contracts if strike_min <= contract.strike <= strike_max]
    if liquid_only:
        filtered = [
            contract
            for contract in filtered
            if contract.spread_percentage is not None
            and contract.spread_percentage <= MAX_BID_ASK_SPREAD_PCT
            and contract.midpoint is not None
        ]

    if sort_by == "Strike (low → high)":
        filtered.sort(key=lambda contract: (contract.strike, contract.option_type))
    elif sort_by == "Strike (high → low)":
        filtered.sort(key=lambda contract: (-contract.strike, contract.option_type))
    elif sort_by == "Nearest to spot":
        if spot is not None and spot > 0:
            filtered.sort(key=lambda contract: (abs(contract.strike - spot), contract.strike))
        else:
            filtered.sort(key=lambda contract: contract.strike)
    elif sort_by == "Highest volume":
        filtered.sort(key=lambda contract: (-(contract.volume or 0), contract.strike))
    elif sort_by == "Highest open interest":
        filtered.sort(key=lambda contract: (-(contract.open_interest or 0), contract.strike))
    elif sort_by == "Tightest spread":
        filtered.sort(
            key=lambda contract: (
                contract.spread_percentage if contract.spread_percentage is not None else float("inf"),
                contract.strike,
            )
        )

    return filtered


def build_contract_comparisons(
    chain_frames: dict[str, pd.DataFrame],
    *,
    option_type: OptionType,
    spot: float,
    target_strike: float,
    target_days_to_expiration: int,
    volatility: float,
    risk_free_rate: float,
    dividend_yield: float = 0.0,
    day_count_basis: int = 365,
    max_spread_pct: float = MAX_BID_ASK_SPREAD_PCT,
    max_contracts: int = MAX_DISPLAY_CONTRACTS,
    as_of: date | None = None,
) -> list[OptionContractComparison]:
    """
    Filter, price, rank, and highlight listed contracts across one or more expirations.

    ``chain_frames`` maps expiration date strings to Yahoo chain DataFrames for the
    selected option side (calls or puts).
    """
    candidates: list[tuple[float, OptionContractComparison]] = []

    for expiration_date, chain_df in chain_frames.items():
        if chain_df is None or chain_df.empty:
            continue

        for _, row in chain_df.iterrows():
            normalized = normalize_chain_row(
                row,
                option_type=option_type,
                expiration_date=expiration_date,
                as_of=as_of,
            )
            strike = normalized["strike"]
            bid = normalized["bid"]
            ask = normalized["ask"]
            midpoint = normalized["midpoint"]
            spread_pct = normalized["spread_percentage"]

            if strike is None or strike <= 0:
                continue
            if not passes_liquidity_filters(bid, ask, midpoint, spread_pct, max_spread_pct=max_spread_pct):
                continue

            days = normalized["days_to_expiration"]
            time_to_expiry = years_from_days(days, basis=day_count_basis)
            theoretical = _theoretical_price(
                option_type=option_type,
                spot=spot,
                strike=strike,
                time_to_expiry=time_to_expiry,
                volatility=volatility,
                risk_free_rate=risk_free_rate,
                dividend_yield=dividend_yield,
            )
            absolute_difference, percentage_difference, model_edge = _comparison_metrics(
                theoretical,
                midpoint,
                ask,
            )

            contract = OptionContractComparison(
                contract_symbol=normalized["contract_symbol"],
                option_type=option_type,
                expiration_date=expiration_date,
                days_to_expiration=days,
                strike=strike,
                bid=bid,
                ask=ask,
                midpoint=midpoint,
                last_price=normalized["last_price"],
                implied_volatility=normalized["implied_volatility"],
                volume=normalized["volume"],
                open_interest=normalized["open_interest"],
                spread_percentage=spread_pct,
                theoretical_price=theoretical,
                absolute_difference=absolute_difference,
                percentage_difference=percentage_difference,
                model_edge=model_edge,
            )
            score = _rank_score(
                strike=strike,
                target_strike=target_strike,
                spot=spot,
                days=days,
                target_days=target_days_to_expiration,
                volume=contract.volume,
                open_interest=contract.open_interest,
                spread_pct=spread_pct,
            )
            candidates.append((score, contract))

    candidates.sort(key=lambda item: item[0])
    selected = [contract for _, contract in candidates[:max_contracts]]
    return _apply_highlights(selected)


def _apply_highlights(contracts: list[OptionContractComparison]) -> list[OptionContractComparison]:
    if not contracts:
        return []

    closest_id = None
    closest_pct = None
    for contract in contracts:
        if contract.percentage_difference is None:
            continue
        if closest_pct is None or contract.percentage_difference < closest_pct:
            closest_pct = contract.percentage_difference
            closest_id = contract.contract_symbol

    edge_id = None
    edge_value = None
    for contract in contracts:
        if contract.model_edge is None or contract.model_edge <= 0:
            continue
        if edge_value is None or contract.model_edge > edge_value:
            edge_value = contract.model_edge
            edge_id = contract.contract_symbol

    highlighted: list[OptionContractComparison] = []
    for contract in contracts:
        highlighted.append(
            replace(
                contract,
                is_closest_to_model=contract.contract_symbol == closest_id and closest_id is not None,
                has_highest_model_edge=contract.contract_symbol == edge_id and edge_id is not None,
            )
        )
    return highlighted


def expirations_near_target(
    all_expirations: list[str],
    target_expiration: str,
    *,
    max_day_distance: int = 21,
) -> list[str]:
    """Return listed expirations within ``max_day_distance`` calendar days of ``target_expiration``."""
    if not all_expirations or not target_expiration:
        return []

    target_date = datetime.strptime(target_expiration, "%Y-%m-%d").date()
    nearby: list[str] = []
    for expiration in all_expirations:
        exp_date = datetime.strptime(expiration, "%Y-%m-%d").date()
        if abs((exp_date - target_date).days) <= max_day_distance:
            nearby.append(expiration)
    return sorted(set(nearby))
