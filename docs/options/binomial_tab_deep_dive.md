# Binomial Tab Deep Dive

This document explains the Binomial tab end to end: what every section means,
where each value comes from, why the model generates the displayed results, how
the binomial tree is built, how simulation works, and how to validate the output
against live option-chain data and external calculators.

The goal is not just to explain the code. The goal is to explain the financial
model, the data flow, and the reasoning behind every displayed number.

## High-Level Purpose

The Binomial tab answers this question:

> Given a current underlying price, a strike, an expiration, volatility, rates,
> dividends, and an exercise style, what should this option be worth under a
> Cox-Ross-Rubinstein binomial tree?

The tab also answers related validation questions:

- What does the live option chain say the contract is trading around?
- How far is the model value from the bid/ask midpoint?
- What volatility would make the binomial model match the live market midpoint?
- Does the binomial value agree with Black-Scholes when the option is European?
- Does a Monte Carlo simulation produce a similar European payoff value?
- Are the binomial tree internals valid, especially the risk-neutral probability?

The app is built for research and model validation. Yahoo Finance data can be
delayed, cached, or missing. The model can be mathematically valid while the
market data is stale.

## Main Sections in the Tab

The Binomial tab has these functional areas:

- Header and model description.
- Ticker and refresh controls.
- Quote strip for the underlying.
- Contract panel.
- Model assumptions panel.
- External calculator comparison panel.
- Results tab.
- Tree Visualizer tab.
- Simulation tab.
- Validation Notes tab.

Each one is explained below.

## Header and Model Description

The header states that the tab uses a Cox-Ross-Rubinstein lattice.

That matters because there are many binomial models. This implementation uses
CRR, where:

```text
u = exp(sigma * sqrt(dt))
d = 1 / u
```

The tree recombines because `u * d = 1`. This makes the tree efficient and
stable for vanilla options.

The header also states that the page uses:

- Yahoo Finance quote snapshots.
- Yahoo Finance option-chain snapshots.
- Binomial model pricing.
- Black-Scholes comparison.
- External calculator comparison.
- Monte Carlo sanity checks.

These are separate validation layers. The app does not assume one output is
automatically correct.

## Ticker and Refresh Controls

### Ticker

The ticker input is passed to Yahoo Finance through `yfinance`.

Examples:

```text
AAPL
SPY
MSFT
TSLA
```

The ticker is used for:

- Underlying quote lookup.
- Available option expiration lookup.
- Option-chain lookup for the selected expiration.

### Refresh Market Data

The refresh button clears the cached quote, expiration, and option-chain calls.

The app caches market data briefly because repeated Yahoo requests can be slow
or rate-limited. Refresh forces the app to ask Yahoo again.

Important:

Refreshing data does not make Yahoo data exchange-real-time. It only refreshes
the app's local cached snapshot.

## Underlying Quote Strip

The quote strip shows:

- Underlying ticker.
- Last underlying price.
- Previous close.
- Day range.
- Source and cache information.
- Move versus previous close.

### Where the Quote Comes From

The app first tries Yahoo `fast_info`.

If that does not return a usable price, it falls back to recent one-minute
history:

```text
ticker.history(period="1d", interval="1m")
```

The quote is used as the model's spot price when `Use latest underlying price`
is enabled.

### Why Spot Price Matters

The spot price is `S0`, the starting point of the binomial tree.

Every future node is generated from this value:

```text
S(i, j) = S0 * u^j * d^(i - j)
```

If spot is wrong, every node in the tree is wrong.

Example:

```text
S0 = 100
u = 1.02
d = 0.980392
```

Then:

```text
Step 1 up   = 100 * 1.02     = 102.00
Step 1 down = 100 * 0.980392 = 98.04
```

## Contract Panel

The Contract panel defines the option being priced.

### Option Type

The app supports:

- Call
- Put

A call payoff at expiration is:

```text
max(S_T - K, 0)
```

A put payoff at expiration is:

```text
max(K - S_T, 0)
```

Where:

- `S_T` is terminal stock price.
- `K` is strike.

### Exercise Style

The app supports:

- American
- European

European options can exercise only at expiration.

American options can exercise at any node before expiration.

In the tree, this changes the backward induction formula.

European:

```text
node_value = continuation_value
```

American:

```text
node_value = max(intrinsic_value, continuation_value)
```

This is why the binomial model is useful. Black-Scholes handles European
exercise in closed form, but early exercise needs a tree or another numerical
method.

### Expiration

The app gets available expirations from:

```text
yf.Ticker(symbol).options
```

The selected expiration determines the default number of days until expiration:

```text
days_to_expiry = expiration_date - today
```

The user can override `Days until expiration` manually after selecting an
expiration.

### Strike From Option Chain

After selecting expiration, the app fetches:

```text
yf.Ticker(symbol).option_chain(expiration)
```

Yahoo returns separate DataFrames:

- `calls`
- `puts`

The app uses the selected option type to choose the relevant chain.

If `Call` is selected, strikes come from `calls`.

If `Put` is selected, strikes come from `puts`.

The strike dropdown chooses an existing listed contract. The numeric strike box
then lets the user override that strike if needed.

### Strike Price

Strike is `K`.

It affects:

- Terminal payoff.
- Intrinsic value.
- Moneyness.
- Delta and gamma.
- Probability of finishing in the money.

Call intrinsic value:

```text
max(S - K, 0)
```

Put intrinsic value:

```text
max(K - S, 0)
```

Example:

```text
S = 100
K = 105
```

Call intrinsic:

```text
max(100 - 105, 0) = 0
```

Put intrinsic:

```text
max(105 - 100, 0) = 5
```

### Days Until Expiration

Days are converted into annual time `T`.

Calendar basis:

```text
T = days / 365
```

Trading-day basis:

```text
T = days / 252
```

Example:

```text
days = 30
calendar T = 30 / 365 = 0.0821918
trading T  = 30 / 252 = 0.1190476
```

This materially changes option price. Longer `T` usually increases time value.

## Contract Snapshot Cards

After a listed option is selected, the app displays:

- Bid
- Ask
- Last
- Mid
- Chain IV
- Open Interest

### Bid

The bid is the highest displayed price someone is currently willing to pay for
the option.

Source:

```text
option_chain.calls["bid"]
```

or:

```text
option_chain.puts["bid"]
```

### Ask

The ask is the lowest displayed price someone is currently willing to sell the
option for.

Source:

```text
option_chain.calls["ask"]
```

or:

```text
option_chain.puts["ask"]
```

### Last

Last is the last traded option price reported by Yahoo.

It can be stale. If a contract has not traded recently, last can be much less
useful than bid/ask.

### Mid

The app calculates mid as:

```text
mid = (bid + ask) / 2
```

Only if both bid and ask are positive.

If bid/ask are missing or unusable, the app falls back to last:

```text
mid = last
```

The mid is used as the market comparison target.

### Chain IV

Chain IV is Yahoo's implied volatility field:

```text
option_chain.calls["impliedVolatility"]
```

or:

```text
option_chain.puts["impliedVolatility"]
```

It is used as the default volatility input when available.

This does not mean Yahoo's IV was calculated with the same model, day count, or
dividend convention as this app. It is a useful market reference, not a proof.

### Open Interest

Open interest is the number of open contracts reported for the option.

It does not enter the pricing formula. It helps judge liquidity and contract
relevance.

## Model Assumptions Panel

The Model Assumptions panel controls the valuation model.

### Underlying Price Input

If `Use latest underlying price` is selected, the model uses the Yahoo quote
snapshot as `S0`.

If unchecked, the user can manually enter spot.

Manual spot is useful for:

- Stress testing.
- Matching an external calculator.
- Pricing hypothetical scenarios.
- Working around stale quote data.

### Volatility

Volatility is annualized and entered as a percent.

The code converts:

```text
54.59% -> 0.5459
```

Volatility determines the size of up/down moves:

```text
u = exp(sigma * sqrt(dt))
d = 1 / u
```

Higher volatility makes `u` larger and `d` smaller. That widens the tree and
usually increases option value because optionality becomes more valuable.

### Risk-Free Rate

The risk-free rate is annualized and entered as a percent.

The code converts:

```text
4.50% -> 0.045
```

The rate affects:

- Risk-neutral probability.
- Discount factor.
- Present value of future payoff.

Risk-neutral probability:

```text
p = (exp((r - q) * dt) - d) / (u - d)
```

Discount factor:

```text
discount = exp(-r * dt)
```

### Dividend Yield

Dividend yield is annualized and entered as a percent.

The code converts:

```text
1.00% -> 0.01
```

Dividend yield reduces the risk-neutral drift of the underlying:

```text
exp((r - q) * dt)
```

Higher dividend yield usually lowers call values and can increase the value of
early exercise for American calls.

### Tree Steps

Tree steps are the number of periods in the binomial tree.

More steps usually means:

- Better convergence.
- More accurate early-exercise boundary.
- More computation.

The number of nodes in a recombining tree is:

```text
total_nodes = (N + 1) * (N + 2) / 2
```

Example:

```text
N = 250
total_nodes = 251 * 252 / 2 = 31,626
```

The app previews only the first few levels visually because showing all nodes
would be unreadable.

### Simulation Paths

Simulation paths control the Monte Carlo validation tab.

More paths usually means:

- Lower standard error.
- More stable simulation price.
- More computation.

Monte Carlo error falls roughly with:

```text
1 / sqrt(paths)
```

So increasing paths from 20,000 to 80,000 cuts standard error roughly in half.

### Day Count Basis

The app supports:

- Calendar days, 365.
- Trading days, 252.

This only affects conversion of days into years:

```text
T = days / basis
```

To compare with an external calculator, the basis must match.

## External Calculator Comparison

The app includes links to external calculators:

- Cboe Options Calculator.
- Pineify Option Pricing Calculator.

The app does not scrape these calculators. Most public calculators do not expose
stable APIs, and scraping them would be fragile.

Instead, the workflow is:

1. Copy the exact inputs from this app.
2. Enter them into the external calculator.
3. Paste the external theoretical value into this app.
4. Compare `Model - external`.

External comparisons are only useful when all assumptions match:

- Spot.
- Strike.
- Days.
- Volatility.
- Risk-free rate.
- Dividend yield.
- Option type.
- Exercise style.
- Tree steps.
- Day-count basis.

## Core Binomial Tree Formula

The app uses the Cox-Ross-Rubinstein tree.

### Step Size

```text
dt = T / N
```

Example:

```text
days = 30
basis = 365
T = 30 / 365 = 0.0821918
N = 250
dt = 0.0821918 / 250 = 0.000328767
```

### Up Factor

```text
u = exp(sigma * sqrt(dt))
```

Example:

```text
sigma = 0.25
dt = 0.000328767
sqrt(dt) = 0.018132
u = exp(0.25 * 0.018132)
u = exp(0.004533)
u = 1.004543
```

### Down Factor

```text
d = 1 / u
```

Example:

```text
d = 1 / 1.004543
d = 0.995478
```

### First Upper and Lower Stock Nodes

If:

```text
S0 = 100
u = 1.004543
d = 0.995478
```

Then:

```text
S_up   = 100 * 1.004543 = 100.4543
S_down = 100 * 0.995478 = 99.5478
```

These are the "upper" and "lower" values in the first tree step.

### Any Node in the Tree

At step `i`, node `j`:

```text
S(i, j) = S0 * u^j * d^(i - j)
```

Example at step 2:

```text
S(2, 0) = S0 * d^2
S(2, 1) = S0 * u^1 * d^1
S(2, 2) = S0 * u^2
```

Because `u * d = 1`, the middle node returns near `S0`.

## Risk-Neutral Probability

The tree does not use real-world probability.

It uses risk-neutral probability:

```text
p = (exp((r - q) * dt) - d) / (u - d)
```

Where:

- `r` is risk-free rate.
- `q` is dividend yield.
- `dt` is one tree step.
- `u` is up factor.
- `d` is down factor.

Example:

```text
r = 0.045
q = 0
dt = 0.000328767
u = 1.004543
d = 0.995478
```

Compute one-step risk-neutral growth:

```text
growth = exp((0.045 - 0) * 0.000328767)
growth = exp(0.000014795)
growth = 1.000014795
```

Then:

```text
p = (1.000014795 - 0.995478) / (1.004543 - 0.995478)
p = 0.5004 approximately
```

Validation:

```text
0 <= p <= 1
```

If `p` is outside this range, the tree is invalid. The app refuses to price.

## Terminal Payoff

At expiration, the option value is known.

Call:

```text
V = max(S_T - K, 0)
```

Put:

```text
V = max(K - S_T, 0)
```

Example:

```text
K = 105
S_T = 110
call = max(110 - 105, 0) = 5
put  = max(105 - 110, 0) = 0
```

## Backward Induction

After terminal values are known, the model walks backward one step at a time.

Continuation value:

```text
continuation = exp(-r * dt) * (p * V_up + (1 - p) * V_down)
```

European node value:

```text
V_node = continuation
```

American node value:

```text
V_node = max(intrinsic_now, continuation)
```

This is how early exercise is handled.

For an American put, if immediate exercise is worth more than holding the
option, the model uses immediate exercise.

## Results Tab

The Results tab includes:

- Binomial value.
- Market mid.
- Model minus mid.
- Black-Scholes benchmark.
- Model minus external.
- Greeks and value breakdown.
- Market calibration.

### Binomial Value

This is the final root node of the tree.

It is the model's estimate of today's option value.

Internally:

```text
result.price
```

### Market Mid

This is the live chain comparison value:

```text
(bid + ask) / 2
```

or last price if bid/ask are unusable.

### Model - Mid

```text
model_edge = binomial_value - market_mid
```

If positive, the model value is above the market midpoint.

If negative, the model value is below the market midpoint.

This is not automatically a trading signal. It may simply mean the volatility,
rate, dividend, timestamp, or model assumptions differ from the market.

### Black-Scholes Benchmark

Black-Scholes is calculated using the same:

- Spot.
- Strike.
- Time.
- Volatility.
- Risk-free rate.
- Dividend yield.
- Option type.

Black-Scholes is a European closed-form benchmark.

For European options, the CRR binomial price should approach Black-Scholes as
steps increase.

For American options, Black-Scholes is not a full replacement because it does
not model early exercise.

### Model - External

This is:

```text
binomial_value - external_price
```

It is only shown when the user enters an external calculator value.

## Greeks and Value Breakdown

The table shows:

- Delta.
- Gamma.
- Vega.
- Theta per day.
- Rho.
- Intrinsic.
- Time value.
- Early exercise premium.

### Delta

Delta is estimated from the first tree step:

```text
delta = (V_up - V_down) / (S_up - S_down)
```

It estimates option price change for a one-dollar underlying move.

### Gamma

Gamma estimates change in delta.

The app uses the second tree level:

```text
delta_up   = (V_uu - V_ud) / (S_uu - S_ud)
delta_down = (V_ud - V_dd) / (S_ud - S_dd)
gamma      = (delta_up - delta_down) / average_stock_gap
```

### Vega

Vega is calculated with finite differences.

The app reprices the option at slightly higher and lower volatility:

```text
vega = (price(sigma + bump) - price(sigma - bump)) / (2 * bump)
```

Then it divides by `100`, so vega means price change per one volatility point.

### Theta Per Day

Theta estimates one calendar day of time decay:

```text
theta = price(T - 1/365) - price(T)
```

If expiration is less than one day away, it compares model value to intrinsic
value.

### Rho

Rho is calculated with finite differences:

```text
rho = (price(r + bump) - price(r - bump)) / (2 * bump)
```

Then it divides by `100`, so rho means price change per one rate point.

### Intrinsic

Intrinsic value is immediate exercise value.

Call:

```text
max(S - K, 0)
```

Put:

```text
max(K - S, 0)
```

### Time Value

```text
time_value = model_price - intrinsic
```

Time value is what remains after intrinsic value.

### Early Exercise Premium

For American options:

```text
early_exercise_premium = American value - European value
```

For European options, this should be zero.

## Market Calibration Section

The Market Calibration section shows:

- Model-implied IV.
- Chain IV.
- Selected IV.
- Model IV minus chain IV.
- Model IV minus selected IV.

### Why Model-Implied IV Exists

If the model price does not match market mid, the most useful question is often:

> What volatility would make this exact binomial model match the market price?

The solver finds `sigma` such that:

```text
binomial_price(sigma) = market_mid
```

It uses bisection.

Simplified:

```text
low_vol = lowest valid vol
high_vol = 500%

repeat:
    mid_vol = (low_vol + high_vol) / 2
    price = binomial_price(mid_vol)

    if price < market_mid:
        low_vol = mid_vol
    else:
        high_vol = mid_vol
```

The result is model-implied IV.

### Why Model IV Can Differ From Chain IV

Differences can come from:

- Yahoo using a different model.
- Different quote timestamp.
- Bid/ask spread.
- Different dividend assumptions.
- Different day count.
- Different risk-free rate.
- Rounding.
- American versus European treatment.
- Stale last price.

## Tree Visualizer Tab

The Tree Visualizer tab shows:

- Tree diagnostics.
- Visual tree graph.
- Node table.

### Up Factor

Displayed as `u`.

Formula:

```text
u = exp(sigma * sqrt(dt))
```

This is the multiplier applied after an up move.

### Down Factor

Displayed as `d`.

Formula:

```text
d = 1 / u
```

This is the multiplier applied after a down move.

### Risk-Neutral Probability

Displayed as `p`.

Formula:

```text
p = (exp((r - q) * dt) - d) / (u - d)
```

The app displays a success message only if:

```text
0 <= p <= 1
```

### Discount

Displayed as one-step discount factor.

Formula:

```text
discount = exp(-r * dt)
```

### dt

Displayed as one time step.

Formula:

```text
dt = T / steps
```

### Visual Tree Graph

The graph displays the first few tree levels.

Each point is a node.

Hover text shows:

- Step.
- Node index.
- Stock price at that node.
- Option value at that node.

Edges connect a node to its down and up child nodes.

The graph does not display the full 250-step tree. That would be visually
unusable. It displays a preview so the model structure can be inspected.

### Node Table

The node table is the same preview in tabular form:

| Step | Node | Stock Price | Option Value |
| --- | --- | --- | --- |

This is useful for checking exact values without hover interaction.

## Simulation Tab

The Simulation tab is not the binomial tree.

It is an independent European payoff sanity check using risk-neutral geometric
Brownian motion.

### Terminal Price Simulation

The model simulates terminal stock prices:

```text
S_T = S0 * exp((r - q - 0.5 * sigma^2) * T + sigma * sqrt(T) * Z)
```

Where:

- `Z` is a standard normal random draw.
- `S0` is current spot.
- `r` is risk-free rate.
- `q` is dividend yield.
- `sigma` is volatility.
- `T` is time in years.

### Simulated Payoff

For each path:

Call:

```text
payoff = max(S_T - K, 0)
```

Put:

```text
payoff = max(K - S_T, 0)
```

### Discounted Average

The simulation price is:

```text
simulation_price = exp(-r * T) * average(payoffs)
```

### Confidence Interval

The app calculates:

```text
standard_error = std(discounted_payoffs) / sqrt(paths)
```

Then:

```text
95% confidence interval = price +/- 1.96 * standard_error
```

### Why Simulation Is Only a Sanity Check

Plain Monte Carlo prices European terminal payoff well.

It does not handle American early exercise because it only looks at final
payoff.

For American simulation, a more advanced method is needed, such as
Longstaff-Schwartz least-squares Monte Carlo.

In this app:

- Binomial tree is the primary American option model.
- Monte Carlo is an independent European validation layer.

## Validation Notes Tab

The Validation Notes tab summarizes the main checks:

- Spot price source.
- Option-chain field source.
- Editable assumptions.
- CRR probability validity.
- European convergence to Black-Scholes.
- American value should be at least European value.
- External calculator assumptions must match.

This is meant to prevent blind trust in a single output number.

## Full Numerical Example

Assume:

```text
S0 = 100
K = 105
days = 30
basis = 365
T = 30 / 365 = 0.0821918
sigma = 25% = 0.25
r = 5% = 0.05
q = 0
N = 250
option = European call
```

Step size:

```text
dt = 0.0821918 / 250
dt = 0.000328767
```

Up and down:

```text
u = exp(0.25 * sqrt(0.000328767))
u = 1.004543 approximately

d = 1 / u
d = 0.995478 approximately
```

First tree nodes:

```text
S_up = 100 * 1.004543 = 100.4543
S_down = 100 * 0.995478 = 99.5478
```

Risk-neutral probability:

```text
growth = exp((0.05 - 0) * 0.000328767)
growth = 1.00001644

p = (growth - d) / (u - d)
p = about 0.5009
```

Terminal call payoff:

```text
max(S_T - 105, 0)
```

Backward induction discounts the expected value at every node until the root
node is reached.

For this example, a high-step CRR European call should be very close to
Black-Scholes. In local validation, this type of setup produced a difference of
only a few thousandths, which is expected convergence behavior.

## Why a Displayed Value Is Generated

If the tab displays:

```text
Binomial value = $3.54
Market mid = $4.20
Model - mid = -$0.66
```

That means:

```text
model_edge = 3.54 - 4.20 = -0.66
```

The model is below market mid with the current assumptions.

Possible reasons:

- Selected volatility is lower than market-implied volatility.
- Bid/ask midpoint is wide.
- Chain IV and model assumptions differ.
- Rate or dividend input differs from market convention.
- Underlying quote and option quote timestamps do not line up.
- The option is American and early exercise assumptions differ.

The next thing to inspect is model-implied IV.

If model-implied IV is:

```text
30.02%
```

and selected IV is:

```text
25.00%
```

Then the market midpoint requires higher volatility than the selected input.
That explains why the model price was below market mid.

## What to Trust Most

Use this hierarchy:

1. Validate inputs first.
2. Validate `p` is between 0 and 1.
3. Check whether chain bid/ask are liquid and reasonable.
4. Compare model value to market mid.
5. Compare model-implied IV to chain IV.
6. For European options, compare CRR to Black-Scholes.
7. Use Monte Carlo as a noisy independent check.
8. Use external calculators only when every assumption matches.

Do not treat one price difference as a signal unless the data and assumptions
have been reconciled.

## Code Locations

Streamlit UI:

```text
src/quant_research/apps/streamlit/pages/binomial.py
```

Pricing engine:

```text
src/quant_research/options/pricing.py
```

Tests:

```text
tests/test_options_pricing.py
tests/test_streamlit_binomial_page.py
```

Existing formula overview:

```text
docs/options/binomial_option_pricing.md
```

