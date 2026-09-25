#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "trial_design.json"
DATA_PATH = ROOT / "synthetic_validation_data.csv"
MAP_PATH = ROOT / "reproducibility" / "data" / "synthetic_map_data.csv"
OUTPUT_DIR = ROOT / "reproducibility" / "outputs"
SUMMARY_PATH = OUTPUT_DIR / "mock_analysis_summary.json"
TABLE_PATH = OUTPUT_DIR / "mock_primary_analysis.csv"
EDGE_PATH = OUTPUT_DIR / "edge_case_checks.csv"
SEED = 20260925


def firth_logistic(
    x: np.ndarray,
    y: np.ndarray,
    max_iter: int = 100,
    tolerance: float = 1e-8,
) -> tuple[np.ndarray, np.ndarray, int]:
    """Fit a small Firth logistic model for sparse-event validation."""
    beta = np.zeros(x.shape[1])
    for iteration in range(1, max_iter + 1):
        eta = x @ beta
        probability = np.clip(1 / (1 + np.exp(-eta)), 1e-8, 1 - 1e-8)
        weight = probability * (1 - probability)
        information = x.T @ (weight[:, None] * x)
        covariance = np.linalg.pinv(information)
        leverage = np.sum((x @ covariance) * x, axis=1) * weight
        adjusted_score = x.T @ (
            y - probability + leverage * (0.5 - probability)
        )
        step = covariance @ adjusted_score
        beta_next = beta + step
        if np.max(np.abs(beta_next - beta)) < tolerance:
            return beta_next, np.sqrt(np.diag(covariance)), iteration
        beta = beta_next
    raise RuntimeError("Firth logistic regression did not converge.")


def generate_synthetic_data(config: dict[str, object]) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    total = int(config["sample_size"]["target_total"])
    site = np.array([f"S{i:02d}" for i in range(1, 11)])
    participants = pd.DataFrame(
        {
            "participant_id": [f"SYN-{i:04d}" for i in range(1, total + 1)],
            "site": np.resize(site, total),
        }
    )
    participants["prior_protamine_risk"] = 0
    for _, indices in participants.groupby("site", sort=True).groups.items():
        ordered = np.array(sorted(indices))
        high_risk_count = 2 * round((0.10 * len(ordered)) / 2)
        high_risk_indices = rng.choice(
            ordered,
            size=high_risk_count,
            replace=False,
        )
        participants.loc[high_risk_indices, "prior_protamine_risk"] = 1
    participants["treatment"] = 0
    for _, indices in participants.groupby(
        ["site", "prior_protamine_risk"], sort=True
    ).groups.items():
        ordered = np.array(sorted(indices))
        assignments = np.resize(np.array([0, 1]), len(ordered))
        rng.shuffle(assignments)
        participants.loc[ordered, "treatment"] = assignments

    participants["treatment_label"] = participants["treatment"].map(
        {0: "placebo", 1: "flurbiprofen_axetil"}
    )
    participants["age_years"] = np.clip(rng.normal(67, 11, total), 20, 89).round(1)
    participants["sex"] = rng.choice(["female", "male"], size=total, p=[0.43, 0.57])
    participants["baseline_map_mmhg"] = np.clip(
        rng.normal(74, 8, total), 52, 105
    ).round(1)
    participants["cpb_minutes"] = np.clip(
        rng.lognormal(math.log(120), 0.35, total), 45, 320
    ).round(0)
    participants["protamine_mg"] = np.clip(
        rng.normal(230, 55, total), 80, 400
    ).round(0)

    logit = (
        -1.905
        - 0.84 * participants["treatment"].to_numpy()
        + 0.75 * participants["prior_protamine_risk"].to_numpy()
        - 0.018 * (participants["baseline_map_mmhg"].to_numpy() - 74)
    )
    probability = 1 / (1 + np.exp(-logit))
    participants["primary_hypotension"] = rng.binomial(1, probability)
    relative_drop = np.where(
        participants["primary_hypotension"].to_numpy() == 1,
        rng.uniform(0.205, 0.40, total),
        rng.uniform(0.02, 0.195, total),
    )
    participants["nadir_map_mmhg"] = (
        participants["baseline_map_mmhg"].to_numpy() * (1 - relative_drop)
    ).round(1)
    participants["relative_map_drop"] = relative_drop.round(4)
    participants["map_below_65"] = (
        participants["nadir_map_mmhg"] < 65
    ).astype(int)
    rescue_probability = np.clip(
        0.05 + 0.67 * participants["primary_hypotension"], 0, 0.9
    )
    participants["haemodynamic_rescue"] = rng.binomial(1, rescue_probability)
    participants["composite_hypotension_or_rescue"] = (
        (participants["primary_hypotension"] == 1)
        | (participants["haemodynamic_rescue"] == 1)
    ).astype(int)
    participants["aki_kdigo"] = rng.binomial(
        1,
        np.clip(
            0.05
            + 0.04 * participants["primary_hypotension"]
            + 0.0002 * (participants["cpb_minutes"] - 120),
            0.01,
            0.30,
        ),
    )
    participants["reoperation_bleeding"] = rng.binomial(1, 0.018, total)
    participants["serious_adverse_event"] = rng.binomial(1, 0.035, total)
    participants["data_origin"] = "SYNTHETIC VALIDATION DATA—NOT CLINICAL DATA"
    return participants


def generate_map_data(participants: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED + 1)
    records: list[dict[str, object]] = []
    times = np.arange(-5, 31, 1)
    for row in participants.itertuples(index=False):
        baseline = float(row.baseline_map_mmhg)
        nadir = float(row.nadir_map_mmhg)
        nadir_time = int(rng.integers(2, 16))
        for minute in times:
            if minute < 0:
                map_value = baseline + rng.normal(0, 1.1)
            else:
                recovery = min(abs(minute - nadir_time) / 18, 1)
                map_value = nadir + (baseline - nadir) * recovery + rng.normal(0, 1.4)
            records.append(
                {
                    "participant_id": row.participant_id,
                    "minute_from_protamine_start": int(minute),
                    "map_mmhg": round(float(map_value), 1),
                    "valid_seconds": 60,
                    "artefact_flag": 0,
                    "data_origin": "SYNTHETIC VALIDATION DATA—NOT CLINICAL DATA",
                }
            )
    return pd.DataFrame.from_records(records)


def standardised_risk_difference(
    data: pd.DataFrame,
    bootstrap_samples: int = 500,
) -> tuple[float, float, float, bool]:
    design = pd.get_dummies(
        data[
            [
                "treatment",
                "site",
                "prior_protamine_risk",
                "baseline_map_mmhg",
            ]
        ],
        columns=["site"],
        drop_first=True,
        dtype=float,
    )
    design = sm.add_constant(design, has_constant="add")
    model = sm.GLM(
        data["primary_hypotension"],
        design,
        family=sm.families.Binomial(),
    ).fit(maxiter=100)

    def margin(fitted: sm.GLM, frame: pd.DataFrame) -> float:
        treatment_frame = frame.copy()
        placebo_frame = frame.copy()
        treatment_frame["treatment"] = 1
        placebo_frame["treatment"] = 0
        return float(
            fitted.predict(treatment_frame).mean()
            - fitted.predict(placebo_frame).mean()
        )

    estimate = margin(model, design)
    rng = np.random.default_rng(SEED + 2)
    bootstrap: list[float] = []
    strata = list(data.groupby(["site", "prior_protamine_risk"]).groups.values())
    for _ in range(bootstrap_samples):
        sampled_indices = np.concatenate(
            [rng.choice(np.array(indices), size=len(indices), replace=True) for indices in strata]
        )
        sampled = data.loc[sampled_indices].reset_index(drop=True)
        sampled_design = pd.get_dummies(
            sampled[
                [
                    "treatment",
                    "site",
                    "prior_protamine_risk",
                    "baseline_map_mmhg",
                ]
            ],
            columns=["site"],
            drop_first=True,
            dtype=float,
        )
        sampled_design = sm.add_constant(sampled_design, has_constant="add")
        sampled_design = sampled_design.reindex(columns=design.columns, fill_value=0)
        try:
            fitted = sm.GLM(
                sampled["primary_hypotension"],
                sampled_design,
                family=sm.families.Binomial(),
            ).fit(maxiter=100)
            bootstrap.append(margin(fitted, sampled_design))
        except (ValueError, np.linalg.LinAlgError):
            continue
    if len(bootstrap) < int(bootstrap_samples * 0.95):
        raise RuntimeError("More than 5% of bootstrap fits failed.")
    lower, upper = np.quantile(bootstrap, [0.025, 0.975])
    return estimate, float(lower), float(upper), bool(model.converged)


def analyse(data: pd.DataFrame) -> dict[str, object]:
    grouped = data.groupby("treatment_label")["primary_hypotension"].agg(["sum", "count"])
    risk_placebo = grouped.loc["placebo", "sum"] / grouped.loc["placebo", "count"]
    risk_fpa = (
        grouped.loc["flurbiprofen_axetil", "sum"]
        / grouped.loc["flurbiprofen_axetil", "count"]
    )
    crude_rd = float(risk_fpa - risk_placebo)
    crude_rr = float(risk_fpa / risk_placebo)
    adjusted_rd, lower, upper, converged = standardised_risk_difference(data)

    continuous_design = pd.get_dummies(
        data[["treatment", "site", "prior_protamine_risk", "baseline_map_mmhg"]],
        columns=["site"],
        drop_first=True,
        dtype=float,
    )
    continuous_design = sm.add_constant(continuous_design, has_constant="add")
    outcome = data["nadir_map_mmhg"] - data["baseline_map_mmhg"]
    continuous_model = sm.OLS(outcome, continuous_design).fit(cov_type="HC3")

    return {
        "data_origin": "SYNTHETIC VALIDATION DATA—NOT CLINICAL DATA",
        "n_total": int(len(data)),
        "events_placebo": int(grouped.loc["placebo", "sum"]),
        "n_placebo": int(grouped.loc["placebo", "count"]),
        "events_fpa": int(grouped.loc["flurbiprofen_axetil", "sum"]),
        "n_fpa": int(grouped.loc["flurbiprofen_axetil", "count"]),
        "risk_placebo": float(risk_placebo),
        "risk_fpa": float(risk_fpa),
        "crude_risk_difference": crude_rd,
        "crude_risk_ratio": crude_rr,
        "adjusted_standardised_risk_difference": adjusted_rd,
        "adjusted_rd_ci_lower": lower,
        "adjusted_rd_ci_upper": upper,
        "primary_model_converged": converged,
        "continuous_treatment_coefficient": float(
            continuous_model.params["treatment"]
        ),
        "continuous_treatment_ci_lower": float(
            continuous_model.conf_int().loc["treatment", 0]
        ),
        "continuous_treatment_ci_upper": float(
            continuous_model.conf_int().loc["treatment", 1]
        ),
    }


def run_edge_cases() -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for name, outcomes in {
        "zero_events_in_treatment": np.array([0] * 40 + [0] * 34 + [1] * 6),
        "single_event_each_arm": np.array([0] * 39 + [1] + [0] * 39 + [1]),
        "no_events_any_arm": np.zeros(80, dtype=int),
    }.items():
        treatment = np.array([1] * 40 + [0] * 40)
        x = np.column_stack([np.ones(80), treatment])
        try:
            coefficients, standard_errors, iterations = firth_logistic(x, outcomes)
            records.append(
                {
                    "scenario": name,
                    "status": "converged",
                    "treatment_log_odds": coefficients[1],
                    "standard_error": standard_errors[1],
                    "iterations": iterations,
                }
            )
        except RuntimeError as error:
            records.append(
                {
                    "scenario": name,
                    "status": str(error),
                    "treatment_log_odds": "",
                    "standard_error": "",
                    "iterations": "",
                }
            )
    return pd.DataFrame.from_records(records)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    participants = generate_synthetic_data(config)
    participants.to_csv(DATA_PATH, index=False)
    generate_map_data(participants).to_csv(MAP_PATH, index=False)
    summary = analyse(participants)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame([summary]).to_csv(TABLE_PATH, index=False)
    edge_results = run_edge_cases()
    edge_results.to_csv(EDGE_PATH, index=False)
    if not summary["primary_model_converged"]:
        raise RuntimeError("Primary synthetic validation model did not converge.")
    if (edge_results["status"] != "converged").any():
        raise RuntimeError("At least one sparse-event edge-case model failed.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
