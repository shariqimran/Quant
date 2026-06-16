# Binomial Option Pricing Model

This document explains the binomial option pricing tab in the Streamlit app.
The focus is the formula logic, model assumptions, data validation, and result
validation workflow. Code structure is included after the math so the model can
be reviewed from first principles before reading implementation details.

## What the Tab Does

The Binomial page prices listed or manually configured options using a
Cox-Ross-Rubinstein binomial tree.

It supports:

- Call and put options.
- American and European exercise styles.
- Yahoo Finance quote snapshots for the underlying.
- Yahoo Finance option-chain fields for expiration, strike, bid, ask, last, and implied volatility.
- Manual overrides for spot, strike, volatility, risk-free rate, dividend yield, days to expiration, day-count basis, and tree steps.
- Comparison against the selected option-chain mid price.
- Solving model-implied volatility from the live option-chain mid price.
- Comparison against Black-Scholes for European-style convergence checks.
- Risk-neutral Monte Carlo simulation for European terminal-payoff sanity checks.
- Manual comparison against external calculators such as Cboe and Pineify.

The page is designed for research and validation. It is not an execution-grade
trading system and it does not guarantee exchange-tick real-time data.

## Model Being Used

The implementation uses the Cox-Ross-Rubinstein, or CRR, binomial model. The
original CRR paper is "Option Pricing: A Simplified Approach" by John Cox,
Stephen Ross, and Mark Rubinstein. The practical idea is simple: instead of
assuming the stock can move continuously, split the time to expiration into a
fixed number of short steps. At each step the stock can move up or down.

As the number of steps increases, the CRR model for a European option should
converge toward the Black-Scholes value when the same assumptions are used.

References:

- Cox, Ross, and Rubinstein paper listing: https://econpapers.repec.org/RePEc%3Aucb%3Acalbrf%3A79
- Cboe options calculator: https://www.cboe.com/education/tools/options-calculator/
- Cboe Options Institute tool page: https://www.cboe.com/optionsinstitute/tools/options_calculator/
- QuantConnect option pricing model docs: https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/options-models/pricing
- Pineify option pricing calculator: https://pineify.app/option-pricing-calculator

## Inputs and Units

The UI accepts values in user-friendly form, but the pricing code converts them
to annualized decimal form.

| UI Input | Internal Meaning | Example |
| --- | --- | --- |
| Underlying price | `S` | `100.00` |
| Strike price | `K` | `105.00` |
| Days until expiration | converted to `T` years | `30 / 365` |
| Volatility | annualized decimal `sigma` | `25%` becomes `0.25` |
| Risk-free rate | continuously compounded annual rate `r` | `4.5%` becomes `0.045` |
| Dividend yield | continuous annual dividend yield `q` | `1.2%` becomes `0.012` |
| Tree steps | number of binomial periods `N` | `250` |

The day-count basis controls how days are converted into years:

```text
T = days_to_expiration / 365
```

or:

```text
T = days_to_expiration / 252
```

Calendar days are the default because option expiration is calendar based.
Trading days can be useful when matching some third-party calculators or
internal workflows. When comparing with another site, the day-count basis must
match or the result will differ.

## Step 1: Split Time into a Tree

The first calculation is the size of one binomial step:

```text
dt = T / N
```

Where:

- `T` is time to expiration in years.
- `N` is the number of tree steps.
- `dt` is the year fraction represented by one step.

If `T = 0.25` years and `N = 250`, then:

```text
dt = 0.25 / 250 = 0.001
```

That means each tree step represents 0.001 years.

## Step 2: Calculate Up and Down Moves

The CRR model chooses up and down factors from volatility:

```text
u = exp(sigma * sqrt(dt))
d = 1 / u
```

Where:

- `u` is the multiplier after an up move.
- `d` is the multiplier after a down move.
- `sigma` is annualized volatility.
- `sqrt(dt)` scales annual volatility to one tree step.

Example:

```text
S = 100
sigma = 0.25
dt = 0.001

u = exp(0.25 * sqrt(0.001))
d = 1 / u
```

If the first move is up:

```text
S_up = S * u
```

If the first move is down:

```text
S_down = S * d
```

Because `d = 1 / u`, the tree recombines. An up move followed by a down move
lands at the same price as a down move followed by an up move:

```text
S * u * d = S * d * u = S
```

This recombination is why a large tree can be calculated efficiently.

## Step 3: Risk-Neutral Probability

The risk-neutral probability is:

```text
p = (exp((r - q) * dt) - d) / (u - d)
```

Where:

- `r` is the risk-free rate.
- `q` is the dividend yield.
- `exp((r - q) * dt)` is the risk-neutral expected stock growth over one step.
- `p` is the model probability assigned to the up branch.
- `1 - p` is the model probability assigned to the down branch.

This `p` is not a forecast that the stock will actually go up. It is the
risk-neutral probability that makes the tree arbitrage-free under the model.

The model validates:

```text
0 <= p <= 1
```

If `p` is outside that range, the selected assumptions do not create a valid CRR
tree. The app refuses to price because a number produced from an invalid tree is
not defensible.

Common causes of invalid `p`:

- Too few tree steps.
- Very low volatility.
- Very high dividend yield.
- Rate and dividend assumptions inconsistent with the selected time step.

Practical fix:

- Increase tree steps.
- Review volatility.
- Review dividend yield and risk-free rate.

## Step 4: Build the Stock Price Tree

At step `i`, each node has a number of up moves `j`. The stock price at that
node is:

```text
S(i, j) = S0 * u^j * d^(i - j)
```

Where:

- `S0` is current spot.
- `i` is the step number.
- `j` is the number of up moves.
- `i - j` is the number of down moves.

For a two-step tree:

```text
Step 0:
S

Step 1:
S*d, S*u

Step 2:
S*d*d, S*u*d, S*u*u
```

The middle node recombines because `u*d = d*u`.

## Step 5: Calculate Terminal Payoff

At expiration, the option value is its intrinsic payoff.

For a call:

```text
call_payoff = max(S_terminal - K, 0)
```

For a put:

```text
put_payoff = max(K - S_terminal, 0)
```

This is calculated at every final stock-price node.

## Step 6: Roll Backward Through the Tree

After terminal payoffs are known, the model works backward to today.

The one-step discount factor is:

```text
discount = exp(-r * dt)
```

For each earlier node:

```text
continuation = discount * (p * option_up + (1 - p) * option_down)
```

For a European option:

```text
node_value = continuation
```

For an American option:

```text
exercise_value = intrinsic value at this node
node_value = max(exercise_value, continuation)
```

This is the key difference between European and American options.

European options can only exercise at expiration, so early exercise is not
available.

American options can exercise at any node. Because of that extra right, an
American option should be worth at least as much as the comparable European
option:

```text
American value >= European value
```

The app calculates and displays:

```text
early_exercise_premium = American value - European value
```

For many non-dividend-paying calls this premium is usually zero. For puts, or
dividend-paying calls, early exercise can matter.

## Greeks

The page displays these Greeks:

- Delta
- Gamma
- Vega
- Theta per day
- Rho

### Delta

Delta estimates how much the option price changes for a one-dollar move in the
underlying.

In a binomial tree, root delta can be estimated from the first up and down nodes:

```text
delta = (option_up - option_down) / (stock_up - stock_down)
```

### Gamma

Gamma estimates how much delta changes as spot changes.

The implementation estimates two deltas from the second tree level and compares
them:

```text
delta_up   = (option_uu - option_ud) / (stock_uu - stock_ud)
delta_down = (option_ud - option_dd) / (stock_ud - stock_dd)
gamma      = (delta_up - delta_down) / average_stock_gap
```

### Vega

Vega estimates price sensitivity to volatility.

Binomial trees do not have a simple closed-form vega, so the implementation uses
a controlled finite difference:

```text
vega = (price(sigma + bump) - price(sigma - bump)) / (2 * bump)
```

The result is divided by `100` so it means the option price change for a one
percentage-point volatility move.

Example:

```text
sigma = 25%
one volatility point = 26% - 25%
```

### Theta

Theta estimates one calendar day of time decay.

The implementation calculates:

```text
theta_per_day = price(T - 1/365) - price(T)
```

If there is less than one day left, it compares the model value to intrinsic
value.

### Rho

Rho estimates price sensitivity to the risk-free rate.

The implementation uses finite differences:

```text
rho = (price(r + bump) - price(r - bump)) / (2 * bump)
```

The result is divided by `100` so it means the option price change for a one
percentage-point rate move.

## Zero Volatility Case

The standard CRR formula uses:

```text
u = exp(sigma * sqrt(dt))
d = 1 / u
```

If `sigma = 0`, then:

```text
u = 1
d = 1
```

The risk-neutral probability formula would divide by zero because `u - d = 0`.

The implementation handles this separately. With zero volatility, the stock path
is deterministic under the risk-neutral drift:

```text
growth = exp((r - q) * dt)
```

The model rolls backward through this deterministic path and still applies
American early-exercise checks when the selected style is American.

## Live Data and Validation

The app uses `yfinance` for market data.

Quote data:

- First tries Yahoo `fast_info`.
- Falls back to recent one-minute Yahoo history if needed.
- Uses a short cache TTL.

Option-chain data:

- Pulls available expirations from Yahoo.
- Pulls calls and puts for the selected expiration.
- Uses the selected chain row for strike, bid, ask, last, implied volatility, and open interest.

The market mid is:

```text
mid = (bid + ask) / 2
```

If bid or ask is missing or zero, the app falls back to last traded price.

Important limitation:

Yahoo Finance data can be delayed, cached, rate-limited, or missing. The model
can validate formulas and internal consistency, but it cannot guarantee that the
input quote is exchange-tick real-time.

## Best Practical Workflow With Live Data

For live or near-live option pricing, the strongest workflow is not simply
"calculate a price and hope it matches the market." A better workflow is:

1. Pull the current underlying quote.
2. Pull the current option-chain bid, ask, last, and implied volatility.
3. Use the bid/ask midpoint as the live market option value when bid and ask are usable.
4. Price the option with the selected model and the selected volatility.
5. Compare model value to market midpoint.
6. Solve the model-implied volatility from the live midpoint.
7. Compare solved model IV to chain IV.
8. For European settings, compare binomial value to Black-Scholes.
9. Run a seeded Monte Carlo simulation as a noisy independent sanity check.
10. Compare with a third-party calculator only after matching every assumption.

The app now follows this workflow.

Why solving IV matters:

If the model price and market mid differ, the market is usually not "wrong."
The most likely explanation is that the volatility input is not the same
volatility implied by the live option price. Solving model IV answers:

> What volatility would make this model reproduce the current market midpoint?

That value is then compared with Yahoo's chain IV and the user-selected IV.

## Model-Implied Volatility

The model-implied volatility solver uses the binomial model itself.

Given:

```text
target_price = live option midpoint
```

The solver searches for `sigma` such that:

```text
binomial_price(sigma) = target_price
```

The implementation uses bisection:

```text
low_sigma  = lowest valid volatility
high_sigma = high volatility bound

repeat:
    mid_sigma = (low_sigma + high_sigma) / 2
    price = binomial_price(mid_sigma)

    if price is close to target:
        return mid_sigma
    if price < target:
        low_sigma = mid_sigma
    else:
        high_sigma = mid_sigma
```

The lower bound is not assumed to be valid. For a finite CRR tree, very low
volatility can make the risk-neutral probability invalid. The solver increases
the lower volatility until the CRR tree has a valid `p`.

If the target price is outside the feasible model range, the solver returns no
IV instead of showing a misleading value.

## Monte Carlo Simulation Check

The Simulation tab uses risk-neutral geometric Brownian motion:

```text
S_T = S_0 * exp((r - q - 0.5 * sigma^2) * T + sigma * sqrt(T) * Z)
```

Where:

- `Z` is a standard normal random number.
- `S_T` is the simulated terminal stock price.
- `r` is risk-free rate.
- `q` is dividend yield.
- `sigma` is annualized volatility.
- `T` is time to expiration.

Terminal payoff is:

```text
call = max(S_T - K, 0)
put  = max(K - S_T, 0)
```

The simulated option value is:

```text
MC price = exp(-rT) * average(payoff)
```

The app also displays a 95% confidence interval:

```text
standard_error = std(discounted_payoffs) / sqrt(paths)
CI = price +/- 1.96 * standard_error
```

Important limitation:

This Monte Carlo check is for European terminal payoff. It is not an American
early-exercise model. American Monte Carlo requires a more complex method such
as Longstaff-Schwartz regression. For American vanilla options, the binomial
tree remains the primary model in this app.

## Result Validation Workflow

Use this checklist when validating a price.

1. Select the ticker.
2. Refresh market data.
3. Confirm the displayed spot price.
4. Select the exact expiration.
5. Select the exact strike.
6. Confirm option type: call or put.
7. Confirm exercise style: American or European.
8. Confirm volatility. If using option-chain IV, verify the displayed IV.
9. Confirm risk-free rate.
10. Confirm dividend yield.
11. Confirm day-count basis.
12. Confirm tree steps.
13. Check that `0 <= p <= 1`.
14. Compare model value to option-chain mid.
15. Review model-implied IV from the live market mid.
16. Compare model-implied IV to Yahoo chain IV.
17. For European options, increase steps and verify convergence toward Black-Scholes.
18. Use the Simulation tab as a noisy independent European payoff check.
19. Open an external calculator and copy the same inputs.
20. Paste the external theoretical price into the app.
21. Review the `Model - external` difference.

## Why Results Can Differ From Another Website

Different calculators can produce different prices even with similar inputs.
Common reasons:

- One site uses calendar days and another uses trading days.
- One site uses discrete dividends and another uses continuous dividend yield.
- One site uses American exercise and another uses European exercise.
- One site uses CRR while another uses a different binomial tree.
- One site uses fewer or more tree steps.
- One site rounds volatility, rate, or time differently.
- One site uses delayed market data from a different timestamp.
- One site uses bid, ask, mid, or last as the underlying input.
- One site uses a different risk-free curve.

For a fair comparison, match every input exactly.

## Code Map

Pricing engine:

```text
src/quant_research/options/pricing.py
```

Main function:

```python
calculate_binomial_option(...)
```

This function:

- Validates spot, strike, time, volatility, steps, option type, and exercise style.
- Calculates `dt`, `u`, `d`, `p`, and discount factor.
- Rejects invalid risk-neutral probability.
- Builds the stock tree.
- Calculates terminal payoffs.
- Rolls option values backward.
- Applies American early-exercise checks.
- Calculates Greeks and tree diagnostics.
- Returns a `BinomialResult`.

Streamlit page:

```text
src/quant_research/apps/streamlit/pages/binomial.py
```

This page:

- Renders ticker and refresh controls.
- Fetches quote and option-chain snapshots.
- Allows manual overrides.
- Calls the pricing engine.
- Displays result metrics, Greeks, diagnostics, and validation notes.
- Renders a visual node-link graph of the first tree levels.
- Calibrates binomial implied volatility from selected market midpoint.
- Runs a seeded European Monte Carlo sanity check.
- Provides external calculator links and a manual comparison input.

Tests:

```text
tests/test_options_pricing.py
```

The tests verify:

- European CRR convergence toward Black-Scholes.
- American put value is at least European put value.
- Invalid CRR probabilities are rejected.
- Binomial implied-volatility solving recovers the input volatility.
- Monte Carlo output is statistically close to Black-Scholes for a European call.
- Existing Black-Scholes reference values still pass.

## Practical Interpretation

The binomial model answers this question:

> If the underlying can only move up or down each step, and the expected growth
> is risk-neutral after adjusting for dividends, what option value prevents
> arbitrage?

For European options, the tree is mainly a numerical approximation to the
continuous Black-Scholes model.

For American options, the tree is more useful because it can evaluate early
exercise at every node. That is why this tab is separate from the Black-Scholes
tab.
