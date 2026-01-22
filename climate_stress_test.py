"""
Climate Stress Test (ACPR/BCE-inspired) — Simple academic implementation
-----------------------------------------------------------------------

Reads an Excel file 'portfolio_climat.xlsx' containing:
- Sheet 'Portfolio' (loan-level data)
- Sheet 'Scenario_Uplifts' (sector x scenario uplifts for PD and LGD)

Outputs:
- results_<Scenario>.csv (loan-level results)
- summary_by_sector_<Scenario>.csv
- summary_by_country_<Scenario>.csv
- climate_var_summary.csv

Usage:
    python climate_stress_test.py --input portfolio_climat.xlsx --alpha 0.95

Notes:
- This is a simplified pedagogical model (uplifts are assumed inputs).
- PD is annual, LGD is fraction, EAD in EUR.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


SCENARIOS = ["Optimiste", "Neutre", "Pessimiste"]


@dataclass(frozen=True)
class StressTestConfig:
    alpha: float = 0.95
    cap_pd: float = 1.0


def _require_columns(df: pd.DataFrame, cols: list[str], name: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in {name}: {missing}")


def load_inputs(xlsx_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load Portfolio and Scenario_Uplifts sheets."""
    portfolio = pd.read_excel(xlsx_path, sheet_name="Portfolio")
    uplifts = pd.read_excel(xlsx_path, sheet_name="Scenario_Uplifts")

    _require_columns(
        portfolio,
        ["loan_id", "sector", "country", "region", "EAD_EUR", "PD_base", "LGD", "maturity_years"],
        "Portfolio",
    )
    _require_columns(
        uplifts,
        [
            "sector",
            "pd_uplift_Optimiste", "pd_uplift_Neutre", "pd_uplift_Pessimiste",
            "lgd_uplift_Optimiste", "lgd_uplift_Neutre", "lgd_uplift_Pessimiste",
        ],
        "Scenario_Uplifts",
    )

    # Normalize dtypes
    portfolio["sector"] = portfolio["sector"].astype(str)
    portfolio["country"] = portfolio["country"].astype(str)
    portfolio["region"] = portfolio["region"].astype(str)
    portfolio["EAD_EUR"] = pd.to_numeric(portfolio["EAD_EUR"], errors="raise")
    portfolio["PD_base"] = pd.to_numeric(portfolio["PD_base"], errors="raise")
    portfolio["LGD"] = pd.to_numeric(portfolio["LGD"], errors="raise")
    portfolio["maturity_years"] = pd.to_numeric(portfolio["maturity_years"], errors="raise")

    uplifts["sector"] = uplifts["sector"].astype(str)

    return portfolio, uplifts


def apply_scenario(
    portfolio: pd.DataFrame,
    uplifts: pd.DataFrame,
    scenario: str,
    cfg: StressTestConfig = StressTestConfig(),
) -> pd.DataFrame:
    """Return loan-level dataframe with stressed PD/LGD and projected losses."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{scenario}'. Must be one of: {SCENARIOS}")

    pd_col = f"pd_uplift_{scenario}"
    lgd_col = f"lgd_uplift_{scenario}"

    u = uplifts[["sector", pd_col, lgd_col]].rename(
        columns={pd_col: "pd_uplift", lgd_col: "lgd_uplift"}
    )

    df = portfolio.merge(u, on="sector", how="left")
    if df["pd_uplift"].isna().any() or df["lgd_uplift"].isna().any():
        missing_sectors = df.loc[df["pd_uplift"].isna() | df["lgd_uplift"].isna(), "sector"].unique().tolist()
        raise ValueError(f"Missing uplifts for sectors: {missing_sectors}")

    # Stress PD and LGD (relative uplifts)
    df["PD_stress"] = np.clip(df["PD_base"] * (1.0 + df["pd_uplift"]), 0.0, cfg.cap_pd)
    df["LGD_stress"] = np.clip(df["LGD"] * (1.0 + df["lgd_uplift"]), 0.0, 1.0)

    # Delta PD (only the climate-driven increase)
    df["dPD"] = np.maximum(df["PD_stress"] - df["PD_base"], 0.0)

    # Projected losses (simple stress-test loss proxy)
    # Loss = EAD * dPD * LGD_stress
    df["loss_projected"] = df["EAD_EUR"] * df["dPD"] * df["LGD_stress"]

    # Useful checks / metadata
    df["scenario"] = scenario

    # Reorder
    cols = [
        "scenario", "loan_id", "sector", "country", "region",
        "EAD_EUR", "PD_base", "PD_stress", "dPD",
        "LGD", "LGD_stress",
        "maturity_years",
        "pd_uplift", "lgd_uplift",
        "loss_projected",
    ]
    return df[cols]


def summarize(df: pd.DataFrame, by: str) -> pd.DataFrame:
    """Aggregate projected losses by a dimension (sector/country/region)."""
    g = df.groupby(by, dropna=False).agg(
        n_loans=("loan_id", "count"),
        EAD_EUR=("EAD_EUR", "sum"),
        loss_projected=("loss_projected", "sum"),
        avg_PD_base=("PD_base", "mean"),
        avg_PD_stress=("PD_stress", "mean"),
        avg_LGD=("LGD", "mean"),
        avg_LGD_stress=("LGD_stress", "mean"),
    ).reset_index()

    g["loss_rate_on_EAD"] = np.where(g["EAD_EUR"] > 0, g["loss_projected"] / g["EAD_EUR"], 0.0)
    return g.sort_values("loss_projected", ascending=False)


def climate_var(losses: list[float], alpha: float = 0.95) -> float:
    """Climate VaR: alpha-quantile of scenario losses (loss distribution across scenarios)."""
    arr = np.asarray(losses, dtype=float)
    return float(np.percentile(arr, 100.0 * alpha))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="portfolio_climat.xlsx", help="Path to input Excel file.")
    parser.add_argument("--alpha", type=float, default=0.95, help="VaR confidence level, e.g. 0.95.")
    parser.add_argument("--outdir", type=str, default=".", help="Output directory for CSV results.")
    args = parser.parse_args()

    xlsx_path = Path(args.input).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    cfg = StressTestConfig(alpha=float(args.alpha))

    portfolio, uplifts = load_inputs(xlsx_path)

    # Sanity check: total exposure
    total_ead = float(portfolio["EAD_EUR"].sum())
    print(f"[INFO] Loaded {len(portfolio)} loans | Total EAD = {total_ead:,.0f} EUR")

    scenario_totals = []

    for sc in SCENARIOS:
        df_sc = apply_scenario(portfolio, uplifts, sc, cfg=cfg)

        total_loss = float(df_sc["loss_projected"].sum())
        scenario_totals.append((sc, total_loss))

        # Loan-level results
        df_sc.to_csv(outdir / f"results_{sc}.csv", index=False)

        # Summaries
        summarize(df_sc, "sector").to_csv(outdir / f"summary_by_sector_{sc}.csv", index=False)
        summarize(df_sc, "country").to_csv(outdir / f"summary_by_country_{sc}.csv", index=False)
        summarize(df_sc, "region").to_csv(outdir / f"summary_by_region_{sc}.csv", index=False)

        print(f"[INFO] Scenario {sc}: projected loss = {total_loss:,.0f} EUR")

    # Climate VaR across scenario totals (pedagogical: distribution over NGFS-like scenarios)
    losses_only = [x[1] for x in scenario_totals]
    var_alpha = climate_var(losses_only, alpha=cfg.alpha)

    var_df = pd.DataFrame({
        "scenario": [x[0] for x in scenario_totals],
        "total_loss_projected": losses_only,
    })
    var_df.loc[len(var_df)] = [f"ClimateVaR_{int(cfg.alpha*100)}%", var_alpha]
    var_df.to_csv(outdir / "climate_var_summary.csv", index=False)

    print(f"[INFO] Climate VaR {int(cfg.alpha*100)}% (across scenarios) = {var_alpha:,.0f} EUR")
    print(f"[DONE] Outputs written to: {outdir}")


if __name__ == "__main__":
    main()
