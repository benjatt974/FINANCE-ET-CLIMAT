"""
Central registry of climate indicators.

The final notebook imports INDICATORS from here, so we standardize names once
and everyone codes behind these names in their own module.
"""

def _safe_import(module_path: str, func_names: list[str]):
    """
    Try to import functions. If missing, keep track so the project doesn't crash.
    Returns: (available_dict, missing_list)
    """
    available = {}
    missing = []

    try:
        module = __import__(module_path, fromlist=["*"])
    except Exception as e:
        # module itself missing or has error
        for fn in func_names:
            missing.append(f"{module_path}.{fn} (module error: {e})")
        return available, missing

    for fn in func_names:
        if hasattr(module, fn):
            available[fn] = getattr(module, fn)
        else:
            missing.append(f"{module_path}.{fn} (not found)")

    return available, missing


# --- Official list of indicators (stable API) ---
_SPECS = [
    # Emissions (1–4)
    ("src.emissions", [
        "financed_emissions",
        "portfolio_carbon_intensity",
        "high_emitter_counterparty_share",
        "portfolio_alignment_itr",
    ]),
    # Transition risk (5–8)
    ("src.transition_risk", [
        "sensitive_sector_exposure",
        "non_aligned_loan_share",
        "carbon_price_sensitivity",
        "transition_risk_score",
    ]),
    # Physical risk (9–11)
    ("src.physical_risk", [
        "physical_risk_geo_exposure",
        "high_physical_risk_asset_value",
        "counterparty_climate_resilience_index",
    ]),
    # Climate-related financial risk (12–14)
    ("src.climate_financial_risk", [
        "projected_losses_climate_stress",
        "climate_adjusted_pd",
        "climate_var",
    ]),
    # Green / strategic (15–17)
    ("src.green_indicators", [
        "green_financing_share",
        "green_bond_share",
        "sbti_client_share",
    ]),
]

INDICATORS = {}
MISSING = []

for module_path, funcs in _SPECS:
    ok, missing = _safe_import(module_path, funcs)
    # Store with stable keys "module:function"
    for name, fn in ok.items():
        INDICATORS[name] = fn
    MISSING.extend(missing)


def print_missing():
    """Helper to display what's missing (useful at the beginning of the project)."""
    if not MISSING:
        print("✅ All indicators are available.")
        return
    print("⚠️ Missing / broken indicator functions:")
    for item in MISSING:
        print(" -", item)
