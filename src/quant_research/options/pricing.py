"""Black-Scholes pricing for European options."""

from dataclasses import dataclass
from math import erf, exp, log, pi, sqrt


TRADING_DAYS_PER_YEAR = 252
CALENDAR_DAYS_PER_YEAR = 365


@dataclass(frozen=True)
class BlackScholesResult:
    """Calculated option values and Greeks."""

    call_price: float
    put_price: float
    call_delta: float
    put_delta: float
    gamma: float
    vega: float
    call_theta: float
    put_theta: float
    call_rho: float
    put_rho: float
    call_intrinsic: float
    put_intrinsic: float
    call_time_value: float
    put_time_value: float
    d1: float | None
    d2: float | None


def _norm_cdf(value):
    """Standard normal cumulative distribution function."""
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))


def _norm_pdf(value):
    """Standard normal probability density function."""
    return exp(-0.5 * value * value) / sqrt(2.0 * pi)


def years_from_days(days, basis=CALENDAR_DAYS_PER_YEAR):
    """Convert days to year fraction."""
    if basis <= 0:
        raise ValueError("basis must be positive.")
    return max(float(days), 0.0) / float(basis)


def _validate_inputs(spot, strike, time_to_expiry, volatility):
    if spot <= 0:
        raise ValueError("spot must be positive.")
    if strike <= 0:
        raise ValueError("strike must be positive.")
    if time_to_expiry < 0:
        raise ValueError("time_to_expiry cannot be negative.")
    if volatility < 0:
        raise ValueError("volatility cannot be negative.")


def _deterministic_value(spot, strike, time_to_expiry, risk_free_rate, dividend_yield):
    discounted_spot = spot * exp(-dividend_yield * time_to_expiry)
    discounted_strike = strike * exp(-risk_free_rate * time_to_expiry)
    call_price = max(discounted_spot - discounted_strike, 0.0)
    put_price = max(discounted_strike - discounted_spot, 0.0)
    call_intrinsic = max(spot - strike, 0.0)
    put_intrinsic = max(strike - spot, 0.0)
    return BlackScholesResult(
        call_price=call_price,
        put_price=put_price,
        call_delta=1.0 if call_price > 0 else 0.0,
        put_delta=-1.0 if put_price > 0 else 0.0,
        gamma=0.0,
        vega=0.0,
        call_theta=0.0,
        put_theta=0.0,
        call_rho=0.0,
        put_rho=0.0,
        call_intrinsic=call_intrinsic,
        put_intrinsic=put_intrinsic,
        call_time_value=call_price - call_intrinsic,
        put_time_value=put_price - put_intrinsic,
        d1=None,
        d2=None,
    )


def calculate_black_scholes(
    spot,
    strike,
    time_to_expiry,
    volatility,
    risk_free_rate=0.0,
    dividend_yield=0.0,
):
    """
    Price European call and put options with continuous rates/yields.

    Volatility, risk-free rate, dividend yield, and time are annualized decimals.
    Vega and rho are returned per 1 percentage-point move. Theta is per calendar day.
    """
    spot = float(spot)
    strike = float(strike)
    time_to_expiry = float(time_to_expiry)
    volatility = float(volatility)
    risk_free_rate = float(risk_free_rate)
    dividend_yield = float(dividend_yield)
    _validate_inputs(spot, strike, time_to_expiry, volatility)

    if time_to_expiry == 0 or volatility == 0:
        return _deterministic_value(
            spot,
            strike,
            time_to_expiry,
            risk_free_rate,
            dividend_yield,
        )

    sqrt_time = sqrt(time_to_expiry)
    discount_spot = exp(-dividend_yield * time_to_expiry)
    discount_strike = exp(-risk_free_rate * time_to_expiry)
    d1 = (
        log(spot / strike)
        + (risk_free_rate - dividend_yield + 0.5 * volatility * volatility) * time_to_expiry
    ) / (volatility * sqrt_time)
    d2 = d1 - volatility * sqrt_time

    call_price = spot * discount_spot * _norm_cdf(d1) - strike * discount_strike * _norm_cdf(d2)
    put_price = strike * discount_strike * _norm_cdf(-d2) - spot * discount_spot * _norm_cdf(-d1)

    common_gamma = discount_spot * _norm_pdf(d1) / (spot * volatility * sqrt_time)
    common_theta = -(spot * discount_spot * _norm_pdf(d1) * volatility) / (2.0 * sqrt_time)

    call_theta = (
        common_theta
        - risk_free_rate * strike * discount_strike * _norm_cdf(d2)
        + dividend_yield * spot * discount_spot * _norm_cdf(d1)
    ) / CALENDAR_DAYS_PER_YEAR
    put_theta = (
        common_theta
        + risk_free_rate * strike * discount_strike * _norm_cdf(-d2)
        - dividend_yield * spot * discount_spot * _norm_cdf(-d1)
    ) / CALENDAR_DAYS_PER_YEAR

    call_intrinsic = max(spot - strike, 0.0)
    put_intrinsic = max(strike - spot, 0.0)

    return BlackScholesResult(
        call_price=call_price,
        put_price=put_price,
        call_delta=discount_spot * _norm_cdf(d1),
        put_delta=discount_spot * (_norm_cdf(d1) - 1.0),
        gamma=common_gamma,
        vega=spot * discount_spot * _norm_pdf(d1) * sqrt_time / 100.0,
        call_theta=call_theta,
        put_theta=put_theta,
        call_rho=strike * time_to_expiry * discount_strike * _norm_cdf(d2) / 100.0,
        put_rho=-strike * time_to_expiry * discount_strike * _norm_cdf(-d2) / 100.0,
        call_intrinsic=call_intrinsic,
        put_intrinsic=put_intrinsic,
        call_time_value=call_price - call_intrinsic,
        put_time_value=put_price - put_intrinsic,
        d1=d1,
        d2=d2,
    )
