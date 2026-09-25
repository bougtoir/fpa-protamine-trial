#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "trial_design.json"
RESULTS_PATH = ROOT / "sample_size_results.csv"
REPORT_PATH = ROOT / "sample_size_report.md"
FIGURE_PATH = ROOT / "sample_size_figure.png"
CONSTANTS_PATH = ROOT / "output" / "analysis_constants.json"


def binary_n_per_arm(p_control: float, p_treatment: float, alpha: float, power: float) -> float:
    """Equal-allocation normal approximation for two independent proportions."""
    pooled = (p_control + p_treatment) / 2
    z_alpha = norm.ppf(1 - alpha / 2)
    z_power = norm.ppf(power)
    numerator = (
        z_alpha * math.sqrt(2 * pooled * (1 - pooled))
        + z_power
        * math.sqrt(
            p_control * (1 - p_control)
            + p_treatment * (1 - p_treatment)
        )
    ) ** 2
    return numerator / (p_control - p_treatment) ** 2


def continuous_n_per_arm(delta: float, sd: float, alpha: float, power: float) -> float:
    z_alpha = norm.ppf(1 - alpha / 2)
    z_power = norm.ppf(power)
    return 2 * ((z_alpha + z_power) * sd / delta) ** 2


def inflated_n(raw_n: float, non_evaluable: float) -> int:
    return math.ceil(raw_n / (1 - non_evaluable))


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    sample = config["sample_size"]
    alpha = sample["alpha_two_sided"]
    non_evaluable = sample["non_evaluable_fraction"]

    binary_scenarios = [
        (0.17, 0.05),
        (0.17, 0.07),
        (0.17, 0.08),
        (0.129, 0.05),
        (sample["planning_control_rate"], sample["planning_treatment_rate"]),
        (0.107, 0.05),
    ]
    powers = [0.80, 0.90]
    rows: list[dict[str, object]] = []
    for p_control, p_treatment in binary_scenarios:
        for power in powers:
            raw = binary_n_per_arm(p_control, p_treatment, alpha, power)
            adjusted = inflated_n(raw, non_evaluable)
            rows.append(
                {
                    "outcome_type": "binary",
                    "control_value": p_control,
                    "treatment_value": p_treatment,
                    "effect": p_control - p_treatment,
                    "sd": "",
                    "power": power,
                    "alpha_two_sided": alpha,
                    "raw_n_per_arm": raw,
                    "inflated_n_per_arm": adjusted,
                    "inflated_total_n": adjusted * 2,
                    "selected_basis": (
                        p_control == sample["planning_control_rate"]
                        and p_treatment == sample["planning_treatment_rate"]
                        and power == sample["power"]
                    ),
                }
            )

    for sd in [10.0, 12.0, 15.0]:
        for power in powers:
            raw = continuous_n_per_arm(4.09, sd, alpha, power)
            adjusted = inflated_n(raw, non_evaluable)
            rows.append(
                {
                    "outcome_type": "continuous",
                    "control_value": "",
                    "treatment_value": "",
                    "effect": 4.09,
                    "sd": sd,
                    "power": power,
                    "alpha_two_sided": alpha,
                    "raw_n_per_arm": raw,
                    "inflated_n_per_arm": adjusted,
                    "inflated_total_n": adjusted * 2,
                    "selected_basis": False,
                }
            )

    with RESULTS_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    selected = next(row for row in rows if row["selected_basis"])
    selected_minimum = int(selected["inflated_total_n"])
    target_total = int(sample["target_total"])
    if target_total < selected_minimum:
        raise ValueError(
            f"Configured target total {target_total} is below calculated minimum "
            f"{selected_minimum}."
        )

    report = f"""# Sample-size analysis

## Selected basis

The primary endpoint is the binary 30-minute risk of clinically important
peri-protamine hypotension. The planning control risk is
{sample['planning_control_rate']:.1%}, anchored to a published 12.9% adverse-event
rate during the 30 minutes after protamine administration in patients undergoing
cardiopulmonary bypass. This external estimate does not use the identical endpoint,
so it is treated as a planning anchor rather than validation of the endpoint.
The treatment risk is {sample['planning_treatment_rate']:.1%}; this is materially
more conservative than the zero-event retrospective observation.

Using a two-sided alpha of {alpha:.2f}, {sample['power']:.0%} power, equal
allocation, and the standard normal approximation for two independent
proportions gives {float(selected['raw_n_per_arm']):.1f} evaluable participants
per arm. Allowing {non_evaluable:.0%} for cancelled surgery, absent protamine
exposure, or unusable arterial-line data gives
{int(selected['inflated_n_per_arm'])} per arm
({selected_minimum} total). The operational target is **{target_total}**
participants ({target_total // 2} per arm).

The formula is:

`n = [z_(1-alpha/2)*sqrt(2*p_bar*(1-p_bar)) + z_power*sqrt(p_c*(1-p_c)+p_t*(1-p_t))]^2 / (p_c-p_t)^2`.

## Sensitivity scenarios

The CSV includes all requested 17% versus 5%, 7%, and 8% scenarios at 80%
and 90% power, additional externally anchored scenarios, and continuous-outcome
scenarios for a 4.09-mmHg difference with standard deviations of 10, 12, and
15 mmHg. The binary endpoint determines the target sample size.

## Blinded internal reassessment

Because published protamine studies use heterogeneous event definitions, the
pooled primary-event rate will be reviewed after {sample['blinded_reestimation_after']}
participants have completed the primary window. A statistician who remains
blinded to treatment labels may update the nuisance event-rate assumption using
a prespecified algorithm without examining the treatment effect. Any increase
will require data-monitoring committee recommendation, sponsor approval, ethics
approval where required, registry amendment, and protocol-version control.
No unblinded treatment comparison will be used for this reassessment.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")

    binary_rows = [row for row in rows if row["outcome_type"] == "binary" and row["power"] == 0.90]
    labels = [
        f"{float(row['control_value']):.1%} vs\n{float(row['treatment_value']):.1%}"
        for row in binary_rows
    ]
    totals = [int(row["inflated_total_n"]) for row in binary_rows]
    colors = ["#b8c7d9"] * len(binary_rows)
    selected_index = next(i for i, row in enumerate(binary_rows) if row["selected_basis"])
    colors[selected_index] = "#8b1e3f"
    fig, ax = plt.subplots(figsize=(9, 5.2))
    bars = ax.bar(labels, totals, color=colors, edgecolor="#333333", linewidth=0.7)
    ax.axhline(target_total, color="#8b1e3f", linestyle="--", linewidth=1.5, label=f"Target N={target_total}")
    ax.set_ylabel("Total randomized sample size")
    ax.set_xlabel("Control risk vs treatment risk")
    ax.set_title("Binary primary-endpoint sample-size scenarios (90% power)")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    for bar, total in zip(bars, totals):
        ax.text(bar.get_x() + bar.get_width() / 2, total + max(totals) * 0.015, str(total), ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=300)
    plt.close(fig)

    constants = {
        "calculated_minimum_total": selected_minimum,
        "calculated_minimum_per_arm": int(selected["inflated_n_per_arm"]),
        "target_total": target_total,
        "target_per_arm": target_total // 2,
        "planning_control_rate": sample["planning_control_rate"],
        "planning_treatment_rate": sample["planning_treatment_rate"],
        "alpha_two_sided": alpha,
        "power": sample["power"],
        "non_evaluable_fraction": non_evaluable,
    }
    CONSTANTS_PATH.write_text(json.dumps(constants, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(constants, indent=2))


if __name__ == "__main__":
    main()
