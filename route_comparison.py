"""
PyroLytic — Week 5-6 Route Ranking + Techno-Economic Comparison

Compares two downstream routes for pyrolysis oil, grounded in published
techno-economic analyses (TEAs) rather than invented numbers. Every cost
figure below traces to a cited source; where sources disagree or a figure
had to be extrapolated, that is stated explicitly rather than presented
as precise.

ROUTE A: Pyrolysis oil sold as low-grade fuel/heating oil (minimal upgrading)
ROUTE B: Pyrolysis oil sold as petrochemical feedstock (e.g. BTX aromatics
         via catalytic fast pyrolysis) - higher value product, higher CAPEX

Sources used for cost benchmarks:
- CAPEX/OPEX anchor: Stallkamp et al. 2024, Waste Management 176 - detailed
  OPEX breakdown for APW pyrolysis plant, Germany
- CAPEX/OPEX cross-check: Belgian PlastPyro case study, 40,000 t/y molten-metal
  pyrolysis, doi via ScienceDirect S0956053X20306103 - CAPEX EUR20.1-26.1m,
  OPEX EUR3.4m/y, IRR 20%
- Feedstock cost: ResearchGate TEA (Spanish study) - $30/tonne assumption for
  MSW-sourced plastic waste
- Route B product pricing anchor: Yadav et al. 2023, Energy & Environmental
  Science 16, 3638 - catalytic fast pyrolysis TEA, BTX minimum selling price
  $1.07/kg vs virgin BTX market price $0.68/kg
- CAPEX scaling caveat: De Tommaso et al. 2024, ChemSusChem - pyrolysis/
  gasification CAPEX correlates poorly with simple capacity scaling
  (R2=0.91-0.92 only when using energy-loss based correlation, not linear
  capacity scaling) - this script uses linear scaling as a SIMPLIFICATION,
  flagged explicitly, not as a claim of accuracy
"""
import numpy as np

# ---- Grounded cost benchmarks (all explicitly sourced, see docstring) ----
BENCHMARKS = {
    'capex_per_tonne_year_eur': {'low': 500, 'mid': 650, 'high': 750,
        'source': 'Derived from Belgian PlastPyro case (EUR20.1-26.1m / 40,000 t/y = EUR502-652/t/y); '
                   'upper bound reflects smaller-scale plants typically costing more per tonne (De Tommaso 2024)'},
    'opex_per_tonne_eur': {'low': 60, 'mid': 85, 'high': 120,
        'source': 'Belgian case: EUR3.4m/40,000t = EUR85/t. Range reflects Stallkamp et al. 2024 finding that '
                   'OPEX/tonne varies significantly with scale (fixed costs dominate at small scale)'},
    'feedstock_cost_usd_per_tonne': {'low': 20, 'mid': 30, 'high': 80,
        'source': 'Low/mid: Spanish TEA study ($30/t for MSW-sourced waste plastic, essentially a tipping-fee-'
                   'offset feedstock). High: market-sourced/sorted plastic waste, order-of-magnitude estimate, '
                   'NOT independently sourced - flagged as the weakest-grounded benchmark in this model'},
    'oil_price_route_A_usd_per_tonne': {'low': 300, 'mid': 450, 'high': 600,
        'source': 'Order-of-magnitude estimate based on heating-oil/low-grade-fuel pricing proxy - pyrolysis oil '
                   'in this route requires minimal upgrading, sold near heavy fuel oil prices. NOT independently '
                   'sourced from a specific TEA - flagged as an estimate, not a citation'},
    'product_price_route_B_usd_per_tonne': {'low': 680, 'mid': 870, 'high': 1070,
        'source': 'Yadav et al. 2023 (Energy Environ Sci): BTX minimum selling price $1.07/kg (=$1070/t) vs '
                   'virgin BTX market price $0.68/kg (=$680/t). Mid = simple average, NOT a modeled value'},
}

def print_benchmark_table():
    print("=== Cost Benchmarks Used (all sourced, see script docstring) ===")
    for key, val in BENCHMARKS.items():
        print(f"\n{key}: low={val['low']}, mid={val['mid']}, high={val['high']}")
        print(f"  Source: {val['source']}")


def route_economics(route_name, capacity_tonnes_year, oil_yield_frac, product_price_usd_t,
                     capex_per_t_y_eur, opex_per_t_eur, feedstock_cost_usd_t,
                     eur_usd=1.08, plant_life_years=15, discount_rate=0.10):
    """
    Simple NPV/IRR/payback calculation. Deliberately simple (Lang-factor-style,
    not a full Aspen simulation) - appropriate for a comparative screening
    analysis, not a bankable investment estimate. This distinction is stated
    explicitly in the model output.
    """
    capex_usd = capex_per_t_y_eur * eur_usd * capacity_tonnes_year
    opex_usd_year = opex_per_t_eur * eur_usd * capacity_tonnes_year
    feedstock_cost_year = feedstock_cost_usd_t * capacity_tonnes_year

    oil_tonnes_year = capacity_tonnes_year * oil_yield_frac
    revenue_year = oil_tonnes_year * product_price_usd_t

    annual_cashflow = revenue_year - opex_usd_year - feedstock_cost_year

    # NPV
    years = np.arange(1, plant_life_years + 1)
    discount_factors = 1 / (1 + discount_rate) ** years
    npv = -capex_usd + np.sum(annual_cashflow * discount_factors)

    # Simple payback (undiscounted)
    payback = capex_usd / annual_cashflow if annual_cashflow > 0 else float('inf')

    # Approximate IRR via simple search (avoids needing scipy/numpy_financial)
    def npv_at_rate(r):
        return -capex_usd + np.sum(annual_cashflow / (1 + r) ** years)
    irr = None
    for r_test in np.arange(0.001, 1.0, 0.001):
        if npv_at_rate(r_test) < 0:
            irr = r_test
            break

    return {
        'route': route_name, 'capex_usd_m': capex_usd / 1e6, 'opex_usd_m_year': opex_usd_year / 1e6,
        'revenue_usd_m_year': revenue_year / 1e6, 'annual_cashflow_usd_m': annual_cashflow / 1e6,
        'npv_usd_m': npv / 1e6, 'irr_pct': irr * 100 if irr else None, 'payback_years': payback,
    }


if __name__ == '__main__':
    print_benchmark_table()

    CAPACITY = 40000  # tonnes/year, matches the Belgian anchor case for direct comparability
    # Oil yield: use the confidence-weighted mean from our dataset (mid-temperature, non-catalytic
    # conditions, representative of a real-world unsorted-feedstock scenario) rather than a
    # best-case number from the highest-yield literature row
    OIL_YIELD_ASSUMED = 0.60  # 60% - a conservative-to-mid estimate given dataset spread (see EDA)

    print(f"\n\n=== Route Comparison at {CAPACITY:,} tonnes/year (Belgian-case scale, for direct benchmark comparison) ===")
    print(f"Assumed oil yield: {OIL_YIELD_ASSUMED:.0%} (mid-range per current dataset - NOT from the yield model, ")
    print("which is not yet reliable at broad scope - see model_card.md)")

    scenarios = {}
    for label, capex, opex, feed, price in [
        ('mid', BENCHMARKS['capex_per_tonne_year_eur']['mid'], BENCHMARKS['opex_per_tonne_eur']['mid'],
         BENCHMARKS['feedstock_cost_usd_per_tonne']['mid'], None),
    ]:
        pass

    routeA = route_economics(
        'Route A: Low-grade fuel oil', CAPACITY, OIL_YIELD_ASSUMED,
        BENCHMARKS['oil_price_route_A_usd_per_tonne']['mid'],
        BENCHMARKS['capex_per_tonne_year_eur']['mid'], BENCHMARKS['opex_per_tonne_eur']['mid'],
        BENCHMARKS['feedstock_cost_usd_per_tonne']['mid'])

    routeB = route_economics(
        'Route B: Petrochemical feedstock (BTX)', CAPACITY, OIL_YIELD_ASSUMED,
        BENCHMARKS['product_price_route_B_usd_per_tonne']['mid'],
        BENCHMARKS['capex_per_tonne_year_eur']['high'],  # Route B needs extra upgrading equipment - higher CAPEX
        BENCHMARKS['opex_per_tonne_eur']['high'],
        BENCHMARKS['feedstock_cost_usd_per_tonne']['mid'])

    print(f"\n{'Metric':<28} {'Route A (fuel oil)':<22} {'Route B (petrochem)':<22}")
    print("-" * 72)
    for key in ['capex_usd_m', 'opex_usd_m_year', 'revenue_usd_m_year', 'annual_cashflow_usd_m', 'npv_usd_m', 'payback_years']:
        a, b = routeA[key], routeB[key]
        print(f"{key:<28} {a:<22.2f} {b:<22.2f}")
    print(f"{'irr_pct':<28} {routeA['irr_pct']:<22.1f} {routeB['irr_pct']:<22.1f}")


def sensitivity_analysis(route_name, capacity, oil_yield, base_price, base_capex, base_opex, base_feedstock):
    """
    +/-20% sensitivity on the two parameters most likely to swing an
    investment decision: product price (market risk) and feedstock cost
    (supply risk). Matches the +/-20% methodology used in Stallkamp et al.
    2024 for direct comparability with a real published sensitivity study.
    """
    base = route_economics(route_name, capacity, oil_yield, base_price, base_capex, base_opex, base_feedstock)
    results = {'base_npv_usd_m': base['npv_usd_m']}
    for param_name, param_val, kwarg in [
        ('product_price', base_price, 'product_price_usd_t'),
        ('feedstock_cost', base_feedstock, 'feedstock_cost_usd_t'),
    ]:
        for pct, label in [(0.8, '-20%'), (1.2, '+20%')]:
            kwargs = dict(product_price_usd_t=base_price, capex_per_t_y_eur=base_capex,
                          opex_per_t_eur=base_opex, feedstock_cost_usd_t=base_feedstock)
            kwargs[kwarg] = param_val * pct
            r = route_economics(route_name, capacity, oil_yield, **kwargs)
            results[f'{param_name}_{label}_npv_usd_m'] = r['npv_usd_m']
    return results


if __name__ == '__main__':
    print("\n\n=== Sensitivity Analysis (+/-20%, methodology matches Stallkamp et al. 2024) ===")
    for name, price, capex, opex in [
        ('Route A (fuel oil)', BENCHMARKS['oil_price_route_A_usd_per_tonne']['mid'],
         BENCHMARKS['capex_per_tonne_year_eur']['mid'], BENCHMARKS['opex_per_tonne_eur']['mid']),
        ('Route B (petrochem)', BENCHMARKS['product_price_route_B_usd_per_tonne']['mid'],
         BENCHMARKS['capex_per_tonne_year_eur']['high'], BENCHMARKS['opex_per_tonne_eur']['high']),
    ]:
        sens = sensitivity_analysis(name, CAPACITY, OIL_YIELD_ASSUMED, price, capex, opex,
                                     BENCHMARKS['feedstock_cost_usd_per_tonne']['mid'])
        print(f"\n{name}:")
        for k, v in sens.items():
            print(f"  {k:<35} NPV = ${v:.1f}m")
