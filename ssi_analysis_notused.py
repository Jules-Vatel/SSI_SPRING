#!/usr/bin/env python3
"""
Pre-analysis workflow for the SSI democratic-backsliding survey experiment.

The script:
1. loads a Qualtrics CSV export;
2. removes Qualtrics metadata rows;
3. constructs outcomes, covariates, and treatment indicators;
4. runs balance tests and the pre-registered OLS models;
5. runs ordered-logit robustness checks for governor support; and
6. saves tables and figures to an output directory.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Iterable

VENDOR_DIR = Path(__file__).resolve().parent / "vendor"
if VENDOR_DIR.exists():
    sys.path.insert(0, str(VENDOR_DIR))

LOCAL_CACHE_DIR = Path(__file__).resolve().parent / ".cache"
(LOCAL_CACHE_DIR / "matplotlib").mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(LOCAL_CACHE_DIR / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(LOCAL_CACHE_DIR))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.stats.multitest import multipletests


DEFAULT_INPUT = Path(
    "/Users/tonyzhong/Desktop/UChicago/2025-2026 spring/sosc 133/Offer-Westort_April 28, 2026_08.08.csv"
)
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"

CONDITION_ORDER = [
    "Control",
    "InParty-Policy",
    "InParty-Electoral",
    "InParty-Democracy",
    "OutParty-Policy",
    "OutParty-Electoral",
    "OutParty-Democracy",
]

FRAME_SPEC = 'C(frame, Treatment(reference="Policy"))'
PRIMARY_CONTROL_VAR = "baseline_affpol_abs"

OUTCOME_SPECS = [
    ("governor_support", "Tolerance for future backsliding (re-election support)", "primary"),
    ("affpol_index", "Affective polarization (index)", "primary"),
    ("affpol_latent", "Affective polarization (latent)", "secondary"),
]

SEVEN_POINT_MAP = {
    "very unlikely": 1,
    "unlikely": 2,
    "somewhat unlikely": 3,
    "neither likely nor unlikely": 4,
    "somewhat likely": 5,
    "likely": 6,
    "very likely": 7,
    "very uncomfortable": 1,
    "uncomfortable": 2,
    "somewhat uncomfortable": 3,
    "neither comfortable nor uncomfortable": 4,
    "somewhat comfortable": 5,
    "comfortable": 6,
    "very comfortable": 7,
    "not at all important": 1,
    "low importance": 2,
    "slightly important": 3,
    "moderately important": 4,
    "important": 5,
    "very important": 6,
    "extremely important": 7,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="Path to the Qualtrics CSV export.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where tables and figures will be saved.",
    )
    return parser.parse_args()


def normalize_text(value: object) -> object:
    if pd.isna(value):
        return np.nan
    return str(value).strip()


def normalize_lower(value: object) -> object:
    text = normalize_text(value)
    if pd.isna(text):
        return np.nan
    return str(text).lower()


def map_seven_point(series: pd.Series) -> pd.Series:
    normalized = series.map(normalize_lower)
    mapped = normalized.map(SEVEN_POINT_MAP)
    numeric = pd.to_numeric(series, errors="coerce")
    return mapped.where(mapped.notna(), numeric)


def load_qualtrics_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df = df.replace(r"^\s*$", np.nan, regex=True)

    # Remove the Qualtrics metadata row that stores ImportId values.
    import_mask = df["Status"].astype(str).str.contains(r'^\{"ImportId"', na=False)
    df = df.loc[~import_mask].copy()

    if "Finished" in df.columns:
        df = df.loc[df["Finished"].astype(str).str.upper().eq("TRUE")].copy()
    if "Q-Age" in df.columns:
        df = df.loc[df["Q-Age"] != "Under 18"].copy()

    for column in [
        "Treat_Party",
        "Treat_Frame",
        "InParty",
        "OutParty",
        "GovParty",
        "Q-DemThreat",
        "Q-AttentionCheck",
        "Q-Manipulation Check",
    ]:
        if column in df.columns:
            df[column] = df[column].map(normalize_text)

    return df.reset_index(drop=True)


def compute_party_id_7(row: pd.Series) -> float:
    party = normalize_text(row.get("Q-PartyAffiliation"))
    strength = normalize_text(row.get("Q-PolarAffiliation"))
    lean = normalize_text(row.get("Q-MiddleAffiliation"))

    if party == "Republican":
        return 3 if strength == "Strong" else 2
    if party == "Democrat":
        return -3 if strength == "Strong" else -2
    if lean == "Closer to Republican Party":
        return 1
    if lean == "Closer to Democratic Party":
        return -1
    return 0


def classify_manipulation_response(value: object) -> object:
    text = normalize_lower(value)
    if pd.isna(text):
        return np.nan
    if "electoral advantage" in text or "respond to similar actions" in text:
        return "Electoral"
    if "specific policy outcome" in text:
        return "Policy"
    if "democratic norms and institutions" in text:
        return "Democracy"
    return np.nan


def make_condition_label(row: pd.Series) -> object:
    treat_party = row.get("Treat_Party")
    frame = row.get("frame")
    if treat_party == "Control":
        return "Control"
    if treat_party in {"InParty", "OutParty"} and frame in {"Policy", "Electoral", "Democracy"}:
        return f"{treat_party}-{frame}"
    return np.nan


def compute_latent_score(data: pd.DataFrame, item_cols: list[str]) -> pd.Series:
    items = data[item_cols].astype(float)
    valid = items.dropna()
    if len(valid) < 3:
        return pd.Series(np.nan, index=data.index)

    means = valid.mean()
    stds = valid.std(ddof=0).replace(0, np.nan)
    standardized_valid = ((valid - means) / stds).dropna()
    if standardized_valid.empty:
        return pd.Series(np.nan, index=data.index)

    _, _, vt = np.linalg.svd(standardized_valid.to_numpy(), full_matrices=False)
    loadings = vt[0]
    if loadings.mean() < 0:
        loadings = -loadings

    standardized_all = (items - means) / stds
    scores = standardized_all.fillna(0.0).to_numpy() @ loadings
    score_series = pd.Series(scores, index=data.index, dtype=float)
    score_series.loc[items.notna().sum(axis=1) < 2] = np.nan

    nonmissing = score_series.dropna()
    if nonmissing.empty or np.isclose(nonmissing.std(ddof=0), 0):
        return score_series

    return (score_series - nonmissing.mean()) / nonmissing.std(ddof=0)


def build_analysis_data(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()

    data["republican_therm"] = pd.to_numeric(data["Q-FeelingThermR_1"], errors="coerce")
    data["democratic_therm"] = pd.to_numeric(data["Q-FeelingThermD_1"], errors="coerce")
    data["baseline_affpol_signed"] = data["republican_therm"] - data["democratic_therm"]
    data["baseline_affpol_abs"] = data["baseline_affpol_signed"].abs()

    data["governor_support"] = map_seven_point(data["Q-ReElection"])
    data["baseline_demnorms"] = map_seven_point(data["Q-AffPolarization"])

    social_items = {
        "inlaw_comfort": "Q-InLawDist",
        "friend_comfort": "Q-CloseFriendDist",
        "neighbor_comfort": "Q-Social Distance 3",
    }
    for new_name, old_name in social_items.items():
        data[new_name] = map_seven_point(data[old_name])
        data[f"{new_name}_reversed"] = 8 - data[new_name]

    reversed_items = [
        "inlaw_comfort_reversed",
        "friend_comfort_reversed",
        "neighbor_comfort_reversed",
    ]
    data["affpol_index"] = data[reversed_items].mean(axis=1, skipna=True)
    data.loc[data[reversed_items].notna().sum(axis=1) < 2, "affpol_index"] = np.nan
    data["affpol_latent"] = compute_latent_score(data, reversed_items)

    data["party_id_7pt"] = data.apply(compute_party_id_7, axis=1)

    data["inparty_feeling"] = np.where(
        data["InParty"] == "Republican",
        data["republican_therm"],
        np.where(data["InParty"] == "Democratic", data["democratic_therm"], np.nan),
    )
    data["outparty_feeling"] = np.where(
        data["InParty"] == "Republican",
        data["democratic_therm"],
        np.where(data["InParty"] == "Democratic", data["republican_therm"], np.nan),
    )
    data["baseline_inparty_minus_outparty"] = data["inparty_feeling"] - data["outparty_feeling"]

    data["treated_any"] = (data["Treat_Party"] != "Control").astype(int)
    data["inparty_treat"] = np.where(
        data["Treat_Party"] == "InParty",
        1,
        np.where(data["Treat_Party"] == "OutParty", 0, np.nan),
    )

    data["frame"] = data["Treat_Frame"].map(normalize_text)
    data["selected_action"] = data["Q-DemThreat"].map(normalize_text)
    data["condition_7"] = data.apply(make_condition_label, axis=1)
    data["condition_7"] = pd.Categorical(data["condition_7"], categories=CONDITION_ORDER, ordered=True)

    attention_expected = np.where(data["treated_any"] == 1, data["GovParty"], "Not Specified")
    data["attention_expected"] = attention_expected
    data["attention_pass"] = (data["Q-AttentionCheck"] == data["attention_expected"]).astype(float)

    data["manip_frame_response"] = data["Q-Manipulation Check"].map(classify_manipulation_response)
    data["frame_pass"] = np.where(
        data["treated_any"] == 1,
        (data["manip_frame_response"] == data["frame"]).astype(float),
        np.nan,
    )

    keep_mask = data["condition_7"].notna() & data["selected_action"].notna()
    data = data.loc[keep_mask].copy()

    return data


def save_descriptive_outputs(data: pd.DataFrame, output_dir: Path) -> None:
    condition_counts = (
        data["condition_7"]
        .value_counts(dropna=False)
        .reindex(CONDITION_ORDER)
        .rename_axis("condition_7")
        .reset_index(name="n")
    )
    condition_counts.to_csv(output_dir / "condition_counts.csv", index=False)

    descriptives = (
        data.groupby("condition_7", observed=True)
        .agg(
            n=("condition_7", "size"),
            governor_support_mean=("governor_support", "mean"),
            affpol_index_mean=("affpol_index", "mean"),
            affpol_latent_mean=("affpol_latent", "mean"),
            baseline_affpol_abs_mean=("baseline_affpol_abs", "mean"),
            baseline_affpol_signed_mean=("baseline_affpol_signed", "mean"),
            baseline_demnorms_mean=("baseline_demnorms", "mean"),
            party_id_mean=("party_id_7pt", "mean"),
            inparty_feeling_mean=("inparty_feeling", "mean"),
            outparty_feeling_mean=("outparty_feeling", "mean"),
            attention_pass_rate=("attention_pass", "mean"),
            frame_pass_rate=("frame_pass", "mean"),
        )
        .reindex(CONDITION_ORDER)
        .reset_index()
    )
    descriptives.to_csv(output_dir / "condition_descriptives.csv", index=False)

    selected_action = (
        data["selected_action"]
        .value_counts()
        .rename_axis("selected_action")
        .reset_index(name="n")
    )
    selected_action.to_csv(output_dir / "selected_action_distribution.csv", index=False)

    pd.crosstab(data["condition_7"], data["selected_action"]).to_csv(
        output_dir / "selected_action_by_condition.csv"
    )

    manipulation_summary = (
        data.groupby("condition_7", observed=True)
        .agg(
            attention_pass_rate=("attention_pass", "mean"),
            frame_pass_rate=("frame_pass", "mean"),
        )
        .reindex(CONDITION_ORDER)
        .reset_index()
    )
    manipulation_summary.to_csv(output_dir / "manipulation_checks.csv", index=False)


def is_numeric_series(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def balance_percentage_spreads(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    demographic_vars = ["Q-Age", "Q-Gender", "Q-Race", "Q-PartyAffiliation"]

    for variable in demographic_vars:
        subset = data[["condition_7", variable]].dropna()
        if subset.empty:
            continue

        shares = pd.crosstab(subset["condition_7"], subset[variable], normalize="index")
        for category in shares.columns:
            values = shares[category]
            grand_share = subset[variable].eq(category).mean()
            relative_spread = np.nan
            if grand_share > 0:
                relative_spread = ((values.max() - values.min()) / grand_share) * 100

            rows.append(
                {
                    "variable": variable,
                    "category": category,
                    "min_share": values.min(),
                    "max_share": values.max(),
                    "spread_pp": (values.max() - values.min()) * 100,
                    "relative_spread_pct": relative_spread,
                    "flag_gt_10pp": (values.max() - values.min()) > 0.10,
                    "flag_gt_20pp": (values.max() - values.min()) > 0.20,
                }
            )

    return pd.DataFrame(rows)


def balance_tests(data: pd.DataFrame) -> pd.DataFrame:
    variables = [
        "Q-Age",
        "Q-Gender",
        "Q-Race",
        "Q-PartyAffiliation",
        "party_id_7pt",
        "baseline_affpol_abs",
        "baseline_demnorms",
        "selected_action",
    ]
    rows = []

    for variable in variables:
        subset = data[["condition_7", variable]].dropna()
        if subset.empty:
            continue

        if is_numeric_series(subset[variable]):
            model = smf.ols(f"{variable} ~ C(condition_7)", data=subset).fit()
            anova = sm.stats.anova_lm(model, typ=2)
            stat = anova.loc["C(condition_7)", "F"]
            p_value = anova.loc["C(condition_7)", "PR(>F)"]
            test_type = "omnibus_f_test"
        else:
            contingency = pd.crosstab(subset["condition_7"], subset[variable])
            stat, p_value, _, _ = stats.chi2_contingency(contingency)
            test_type = "chi_square"

        rows.append(
            {
                "variable": variable,
                "test": test_type,
                "statistic": stat,
                "p_value": p_value,
                "n": len(subset),
            }
        )

    return pd.DataFrame(rows)


def fit_ols(formula: str, data: pd.DataFrame):
    return smf.ols(formula=formula, data=data).fit(cov_type="HC2")


def tidy_model(model, model_name: str, outcome: str) -> pd.DataFrame:
    conf = model.conf_int()
    tidy = pd.DataFrame(
        {
            "model": model_name,
            "outcome": outcome,
            "term": model.params.index,
            "estimate": model.params.values,
            "std_error": model.bse.values,
            "p_value": model.pvalues.values,
            "ci_low": conf.iloc[:, 0].values,
            "ci_high": conf.iloc[:, 1].values,
            "nobs": model.nobs,
            "r_squared": getattr(model, "rsquared", np.nan),
        }
    )
    return tidy


def extract_key_term(
    model,
    model_name: str,
    outcome: str,
    family: str,
    term: str,
    label: str,
) -> dict[str, object]:
    conf = model.conf_int()
    return {
        "model": model_name,
        "outcome": outcome,
        "family": family,
        "term": term,
        "label": label,
        "estimate": model.params[term],
        "std_error": model.bse[term],
        "p_value": model.pvalues[term],
        "ci_low": conf.loc[term, 0],
        "ci_high": conf.loc[term, 1],
        "nobs": model.nobs,
    }


def add_holm_adjustments(results: pd.DataFrame) -> pd.DataFrame:
    adjusted = results.copy()
    adjusted["holm_p_value"] = np.nan

    for family, subset in adjusted.groupby("family"):
        if family.startswith(("exploratory", "secondary", "sensitivity")):
            continue
        reject, pvals_adj, _, _ = multipletests(subset["p_value"], method="holm")
        adjusted.loc[subset.index, "holm_p_value"] = pvals_adj
        adjusted.loc[subset.index, "reject_holm_0_05"] = reject

    return adjusted


def run_main_models(
    data: pd.DataFrame,
    control_var: str = PRIMARY_CONTROL_VAR,
    family_prefix: str = "",
    include_secondary: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    formulas = {
        "rq1_any_treatment": f"{{y}} ~ treated_any + {control_var} + baseline_demnorms + party_id_7pt + C(selected_action)",
        "rq2_inparty_vs_outparty": f"{{y}} ~ inparty_treat + {control_var} + baseline_demnorms + party_id_7pt + C(selected_action)",
        "rq3_frame_effects": f'{{y}} ~ {FRAME_SPEC} + inparty_treat + {control_var} + baseline_demnorms + party_id_7pt + C(selected_action)',
        "rq4_frame_x_party": f'{{y}} ~ {FRAME_SPEC} * inparty_treat + {control_var} + baseline_demnorms + party_id_7pt + C(selected_action)',
    }

    full_rows = []
    key_rows = []
    wald_rows = []
    treated = data.loc[data["treated_any"] == 1].copy()

    for outcome_col, outcome_label, outcome_type in OUTCOME_SPECS:
        if outcome_type == "secondary" and not include_secondary:
            continue

        family_tag = "secondary" if outcome_type == "secondary" else family_prefix.rstrip("_")
        rq1_family = f"{family_prefix}rq1_confirmatory" if outcome_type == "primary" else f"{family_tag}_rq1"
        rq2_family = f"{family_prefix}rq2_confirmatory" if outcome_type == "primary" else f"{family_tag}_rq2"
        rq3_family = f"{family_prefix}rq3_confirmatory" if outcome_type == "primary" else f"{family_tag}_rq3"
        rq4_family = f"{family_prefix}exploratory_rq4" if outcome_type == "primary" else f"{family_tag}_rq4"

        full_sample_model = fit_ols(formulas["rq1_any_treatment"].format(y=outcome_col), data)
        full_rows.append(
            tidy_model(
                full_sample_model,
                f"{family_prefix}rq1_any_treatment",
                outcome_label,
            )
        )
        key_rows.append(
            extract_key_term(
                full_sample_model,
                f"{family_prefix}rq1_any_treatment",
                outcome_label,
                rq1_family,
                "treated_any",
                "Any treatment vs control",
            )
        )

        rq2_model = fit_ols(formulas["rq2_inparty_vs_outparty"].format(y=outcome_col), treated)
        full_rows.append(
            tidy_model(
                rq2_model,
                f"{family_prefix}rq2_inparty_vs_outparty",
                outcome_label,
            )
        )
        key_rows.append(
            extract_key_term(
                rq2_model,
                f"{family_prefix}rq2_inparty_vs_outparty",
                outcome_label,
                rq2_family,
                "inparty_treat",
                "In-party vs out-party",
            )
        )

        rq3_model = fit_ols(formulas["rq3_frame_effects"].format(y=outcome_col), treated)
        full_rows.append(tidy_model(rq3_model, f"{family_prefix}rq3_frame_effects", outcome_label))
        electoral_term = f"{FRAME_SPEC}[T.Electoral]"
        democracy_term = f"{FRAME_SPEC}[T.Democracy]"
        key_rows.append(
            extract_key_term(
                rq3_model,
                f"{family_prefix}rq3_frame_effects",
                outcome_label,
                rq3_family,
                electoral_term,
                "Electoral vs policy",
            )
        )
        key_rows.append(
            extract_key_term(
                rq3_model,
                f"{family_prefix}rq3_frame_effects",
                outcome_label,
                rq3_family,
                democracy_term,
                "Democracy vs policy",
            )
        )
        wald_test = rq3_model.t_test(f"{electoral_term} = {democracy_term}")
        wald_rows.append(
            {
                "model": f"{family_prefix}rq3_frame_effects",
                "outcome": outcome_label,
                "control_var": control_var,
                "contrast": "Electoral vs democracy",
                "estimate_difference": float(np.asarray(wald_test.effect).squeeze()),
                "std_error": float(np.asarray(wald_test.sd).squeeze()),
                "t_value": float(np.asarray(wald_test.tvalue).squeeze()),
                "p_value": float(np.asarray(wald_test.pvalue).squeeze()),
            }
        )

        rq4_model = fit_ols(formulas["rq4_frame_x_party"].format(y=outcome_col), treated)
        full_rows.append(tidy_model(rq4_model, f"{family_prefix}rq4_frame_x_party", outcome_label))
        key_rows.append(
            extract_key_term(
                rq4_model,
                f"{family_prefix}rq4_frame_x_party",
                outcome_label,
                rq4_family,
                f"{FRAME_SPEC}[T.Electoral]:inparty_treat",
                "Electoral frame x in-party",
            )
        )
        key_rows.append(
            extract_key_term(
                rq4_model,
                f"{family_prefix}rq4_frame_x_party",
                outcome_label,
                rq4_family,
                f"{FRAME_SPEC}[T.Democracy]:inparty_treat",
                "Democracy frame x in-party",
            )
        )

    full_results = pd.concat(full_rows, ignore_index=True)
    full_results["control_var"] = control_var
    key_results = add_holm_adjustments(pd.DataFrame(key_rows))
    key_results["control_var"] = control_var
    wald_results = pd.DataFrame(wald_rows)
    return full_results, key_results, wald_results


def run_control_sensitivity_models(data: pd.DataFrame) -> pd.DataFrame:
    key_tables = []
    for control_var in ["inparty_feeling", "outparty_feeling"]:
        _, key_results, _ = run_main_models(
            data=data,
            control_var=control_var,
            family_prefix=f"sensitivity_{control_var}_",
            include_secondary=True,
        )
        key_tables.append(key_results)
    return pd.concat(key_tables, ignore_index=True)


def ordered_logit_result(
    data: pd.DataFrame,
    y_col: str,
    x_cols: Iterable[str],
    model_name: str,
    key_terms: list[str],
) -> pd.DataFrame:
    subset = data[[y_col, *x_cols]].dropna().copy()
    endog = subset[y_col].astype(int)
    exog = pd.get_dummies(subset[list(x_cols)], columns=["selected_action"], drop_first=True)
    exog = exog.astype(float)

    model = OrderedModel(endog, exog, distr="logit")
    result = model.fit(method="bfgs", disp=False)
    conf = result.conf_int()

    rows = []
    for term in key_terms:
        rows.append(
            {
                "model": model_name,
                "term": term,
                "estimate": result.params[term],
                "std_error": result.bse[term],
                "p_value": result.pvalues[term],
                "ci_low": conf.loc[term, 0],
                "ci_high": conf.loc[term, 1],
                "nobs": len(subset),
            }
        )
    return pd.DataFrame(rows)


def run_ordered_logit_checks(data: pd.DataFrame) -> pd.DataFrame:
    rows = []

    q1_cols = [
        "treated_any",
        PRIMARY_CONTROL_VAR,
        "baseline_demnorms",
        "party_id_7pt",
        "selected_action",
    ]
    rows.append(
        ordered_logit_result(
            data=data,
            y_col="governor_support",
            x_cols=q1_cols,
            model_name="ordered_logit_rq1",
            key_terms=["treated_any"],
        )
    )

    treated = data.loc[data["treated_any"] == 1].copy()
    q2_cols = [
        "inparty_treat",
        PRIMARY_CONTROL_VAR,
        "baseline_demnorms",
        "party_id_7pt",
        "selected_action",
    ]
    rows.append(
        ordered_logit_result(
            data=treated,
            y_col="governor_support",
            x_cols=q2_cols,
            model_name="ordered_logit_rq2",
            key_terms=["inparty_treat"],
        )
    )

    return pd.concat(rows, ignore_index=True)


def plot_selected_action_distribution(data: pd.DataFrame, output_dir: Path) -> None:
    counts = data["selected_action"].value_counts().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(counts.index, counts.values, color="#5B8E7D")
    ax.set_title("Selected democratic threat")
    ax.set_xlabel("Number of respondents")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(output_dir / "selected_action_distribution.png", dpi=300)
    plt.close(fig)


def outcome_summary_by_condition(data: pd.DataFrame, outcome: str) -> pd.DataFrame:
    summary = (
        data.groupby("condition_7", observed=True)[outcome]
        .agg(["mean", "std", "count"])
        .reindex(CONDITION_ORDER)
        .reset_index()
    )
    summary["se"] = summary["std"] / np.sqrt(summary["count"])
    summary["ci"] = 1.96 * summary["se"]
    return summary


def plot_condition_means(data: pd.DataFrame, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(19, 6))
    plot_specs = [
        ("governor_support", "Tolerance for future backsliding (1-7)", "#3B6EA5"),
        ("affpol_index", "Affective polarization index (1-7)", "#C75B39"),
        ("affpol_latent", "Affective polarization latent score", "#7A4EAB"),
    ]
    display_labels = [
        "Control",
        "In-party\nPolicy",
        "In-party\nElectoral",
        "In-party\nDemocracy",
        "Out-party\nPolicy",
        "Out-party\nElectoral",
        "Out-party\nDemocracy",
    ]

    for ax, (outcome, title, color) in zip(axes, plot_specs):
        summary = outcome_summary_by_condition(data, outcome)
        x = np.arange(len(summary))
        ax.bar(x, summary["mean"], color=color, alpha=0.85)
        ax.errorbar(x, summary["mean"], yerr=summary["ci"], fmt="none", ecolor="black", capsize=4)
        ax.set_xticks(x)
        ax.set_xticklabels(display_labels, rotation=30, ha="right")
        ax.set_title(title)
        ax.set_ylabel("Mean response")

    fig.tight_layout()
    fig.savefig(output_dir / "condition_means.png", dpi=300)
    plt.close(fig)


def plot_key_coefficients(key_results: pd.DataFrame, output_dir: Path) -> None:
    plot_df = key_results.loc[
        key_results["family"].isin(["rq1_confirmatory", "rq2_confirmatory", "rq3_confirmatory"])
        & (key_results["outcome"] != "Affective polarization (latent)")
    ].copy()
    plot_df["display_label"] = plot_df["outcome"] + " | " + plot_df["label"]
    plot_df = plot_df.iloc[::-1].reset_index(drop=True)

    colors = {
        "Tolerance for future backsliding (re-election support)": "#3B6EA5",
        "Affective polarization (index)": "#C75B39",
        "Affective polarization (latent)": "#7A4EAB",
    }

    fig, ax = plt.subplots(figsize=(11, 7))
    y_pos = np.arange(len(plot_df))
    ax.axvline(0, color="gray", linewidth=1, linestyle="--")
    for i, row in plot_df.iterrows():
        ax.errorbar(
            x=row["estimate"],
            y=i,
            xerr=[[row["estimate"] - row["ci_low"]], [row["ci_high"] - row["estimate"]]],
            fmt="o",
            color=colors.get(row["outcome"], "#333333"),
            capsize=4,
        )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(plot_df["display_label"])
    ax.set_xlabel("Coefficient estimate with 95% CI")
    ax.set_title("Main treatment and framing estimates")
    fig.tight_layout()
    fig.savefig(output_dir / "key_coefficients.png", dpi=300)
    plt.close(fig)


def write_run_summary(
    data: pd.DataFrame,
    balance: pd.DataFrame,
    balance_spreads: pd.DataFrame,
    key_results: pd.DataFrame,
    sensitivity_results: pd.DataFrame,
    output_dir: Path,
) -> None:
    lines = [
        "# Run Summary",
        "",
        f"- Analysis sample size: {len(data)}",
        f"- Treated observations: {int(data['treated_any'].sum())}",
        f"- Control observations: {int((data['treated_any'] == 0).sum())}",
        f"- Primary pre-treatment affective-polarization control: `{PRIMARY_CONTROL_VAR}` = |Republican thermometer - Democratic thermometer|",
        f"- Mean attention-check pass rate: {data['attention_pass'].mean():.3f}",
        f"- Mean manipulation-check pass rate among treated: {data.loc[data['treated_any'] == 1, 'frame_pass'].mean():.3f}",
        "",
        "## Balance tests",
        "",
    ]

    for _, row in balance.iterrows():
        lines.append(
            f"- {row['variable']}: {row['test']} statistic={row['statistic']:.3f}, p={row['p_value']:.3f}, n={int(row['n'])}"
        )

    flagged_10 = int(balance_spreads["flag_gt_10pp"].sum()) if not balance_spreads.empty else 0
    flagged_20 = int(balance_spreads["flag_gt_20pp"].sum()) if not balance_spreads.empty else 0
    lines.extend(
        [
            "",
            "## Descriptive balance spread flags",
            "",
            f"- Category cells with more than a 10 percentage-point spread across treatment groups: {flagged_10}",
            f"- Category cells with more than a 20 percentage-point spread across treatment groups: {flagged_20}",
        ]
    )

    lines.extend(["", "## Key confirmatory estimates", ""])
    main_rows = key_results.loc[key_results["family"].isin(["rq1_confirmatory", "rq2_confirmatory", "rq3_confirmatory"])]
    for _, row in main_rows.iterrows():
        holm = row["holm_p_value"]
        holm_text = "NA" if pd.isna(holm) else f"{holm:.3f}"
        lines.append(
            f"- {row['model']} | {row['outcome']} | {row['label']}: b={row['estimate']:.3f}, 95% CI [{row['ci_low']:.3f}, {row['ci_high']:.3f}], p={row['p_value']:.3f}, Holm p={holm_text}"
        )

    latent_rows = key_results.loc[key_results["outcome"] == "Affective polarization (latent)"]
    if not latent_rows.empty:
        lines.extend(["", "## Latent outcome estimates", ""])
        for _, row in latent_rows.iterrows():
            lines.append(
                f"- {row['model']} | {row['label']}: b={row['estimate']:.3f}, 95% CI [{row['ci_low']:.3f}, {row['ci_high']:.3f}], p={row['p_value']:.3f}"
            )

    if not sensitivity_results.empty:
        lines.extend(["", "## Sensitivity control sets", ""])
        for control_var in ["inparty_feeling", "outparty_feeling"]:
            subset = sensitivity_results.loc[
                (sensitivity_results["control_var"] == control_var)
                & sensitivity_results["family"].str.contains("rq1_confirmatory|rq2_confirmatory|rq3_confirmatory")
            ]
            if subset.empty:
                continue
            lines.append(f"- Separate models also estimated with `{control_var}` as the pre-treatment feeling-thermometer control.")

    (output_dir / "run_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = load_qualtrics_csv(args.input)
    data = build_analysis_data(raw)
    data.to_csv(output_dir / "cleaned_analysis_data.csv", index=False)

    save_descriptive_outputs(data, output_dir)

    balance = balance_tests(data)
    balance.to_csv(output_dir / "balance_tests.csv", index=False)
    balance_spreads = balance_percentage_spreads(data)
    balance_spreads.to_csv(output_dir / "balance_percentage_spreads.csv", index=False)

    full_results, key_results, wald_results = run_main_models(data)
    full_results.to_csv(output_dir / "full_regression_results.csv", index=False)
    key_results.to_csv(output_dir / "key_regression_results.csv", index=False)
    wald_results.to_csv(output_dir / "frame_contrast_tests.csv", index=False)
    sensitivity_results = run_control_sensitivity_models(data)
    sensitivity_results.to_csv(output_dir / "control_sensitivity_results.csv", index=False)

    try:
        ordered = run_ordered_logit_checks(data)
        ordered.to_csv(output_dir / "ordered_logit_results.csv", index=False)
    except Exception as exc:  # pragma: no cover - robustness output should not block the main run.
        (output_dir / "ordered_logit_error.txt").write_text(str(exc), encoding="utf-8")

    plot_selected_action_distribution(data, output_dir)
    plot_condition_means(data, output_dir)
    plot_key_coefficients(key_results, output_dir)
    write_run_summary(data, balance, balance_spreads, key_results, sensitivity_results, output_dir)

    metadata = {
        "input_file": str(args.input),
        "output_dir": str(output_dir),
        "primary_control_var": PRIMARY_CONTROL_VAR,
        "analysis_n": int(len(data)),
        "treated_n": int(data["treated_any"].sum()),
        "control_n": int((data["treated_any"] == 0).sum()),
    }
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Saved outputs to {output_dir}")


if __name__ == "__main__":
    main()
