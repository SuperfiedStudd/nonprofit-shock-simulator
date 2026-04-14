from __future__ import annotations

import math
import re
from typing import Any

import numpy as np
import pandas as pd


RISK_BUCKET_ORDER = ["Low", "Watch", "High", "Very High"]
SCENARIO_LABELS = {
    "donation_shock_10": "Donation shock (-10%)",
    "donation_shock_20": "Donation shock (-20%)",
    "donation_shock_30": "Donation shock (-30%)",
    "program_shock_10": "Program revenue shock (-10%)",
    "program_shock_20": "Program revenue shock (-20%)",
    "grant_shock_10": "Grant / government shock (-10%)",
    "grant_shock_20": "Grant / government shock (-20%)",
    "expense_inflation_5": "Expense inflation (+5%)",
    "expense_inflation_10": "Expense inflation (+10%)",
}
SHORTLIST_SECTION_MAP = {
    "Fragile but investable": "Fragile but investable",
    "Resilient outperformer": "Resilient outperformers",
    "Shock-sensitive priority watchlist": "Shock-sensitive watchlist",
}
SIZE_BUCKET_LABELS = {
    "under_1M": "Under $1M",
    "1M_3M": "$1M to $3M",
    "3M_10M": "$3M to $10M",
    "10M_25M": "$10M to $25M",
    "25M_plus": "$25M+",
}
FUNDING_BUCKET_LABELS = {
    "donation_led": "Donation-led",
    "program_led": "Program-led",
    "mixed": "Mixed funding",
}
THRESHOLD_VARIABLES = {
    "reserve_months_proxy",
    "liability_ratio_clean",
    "peer_pct_coverage_obs",
    "peer_pct_margin_obs",
    "revenue_hhi_clean",
}


def _num(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clean_text(value: Any, fallback: str = "Not available") -> str:
    if value is None or pd.isna(value):
        return fallback
    text = str(value).strip()
    return text or fallback


def format_ein(value: Any) -> str:
    digits = "".join(ch for ch in clean_text(value, fallback="") if ch.isdigit())
    if len(digits) != 9:
        return clean_text(value)
    return f"{digits[:2]}-{digits[2:]}"


def format_probability(value: Any) -> str:
    number = _num(value)
    if number is None:
        return "NA"
    return f"{number * 100:.1f}%"


def format_points(value: Any) -> str:
    number = _num(value)
    if number is None:
        return "NA"
    sign = "+" if number >= 0 else ""
    return f"{sign}{number * 100:.1f} pts"


def format_relative(value: Any) -> str:
    number = _num(value)
    if number is None:
        return "NA"
    sign = "+" if number >= 0 else ""
    return f"{sign}{number * 100:.1f}%"


def format_percentile(value: Any) -> str:
    number = _num(value)
    if number is None:
        return "NA"
    return f"{number * 100:.0f}th pct"


def format_ratio(value: Any, digits: int = 2, suffix: str = "x") -> str:
    number = _num(value)
    if number is None:
        return "NA"
    return f"{number:.{digits}f}{suffix}"


def format_months(value: Any) -> str:
    number = _num(value)
    if number is None:
        return "NA"
    return f"{number:.1f} months"


def format_currency_compact(value: Any) -> str:
    number = _num(value)
    if number is None:
        return "NA"
    absolute = abs(number)
    if absolute >= 1_000_000_000:
        return f"${number / 1_000_000_000:.1f}B"
    if absolute >= 1_000_000:
        return f"${number / 1_000_000:.1f}M"
    if absolute >= 1_000:
        return f"${number / 1_000:.0f}K"
    return f"${number:,.0f}"


def format_signed_percent(value: Any) -> str:
    number = _num(value)
    if number is None:
        return "NA"
    sign = "+" if number >= 0 else ""
    return f"{sign}{number * 100:.1f}%"


def risk_bucket_color(bucket: str) -> str:
    return {
        "Low": "#2f7a6b",
        "Watch": "#b98d41",
        "High": "#b7653b",
        "Very High": "#a64743",
    }.get(bucket, "#61788a")


def humanize_size_bucket(value: Any) -> str:
    return SIZE_BUCKET_LABELS.get(clean_text(value, fallback=""), clean_text(value))


def humanize_funding_bucket(value: Any) -> str:
    return FUNDING_BUCKET_LABELS.get(clean_text(value, fallback=""), clean_text(value))


def humanize_peer_group(peer_group: Any) -> str:
    text = clean_text(peer_group)
    if "__" not in text:
        return text
    size_bucket, funding_bucket = text.split("__", 1)
    return f"{humanize_size_bucket(size_bucket)} | {humanize_funding_bucket(funding_bucket)}"


def scenario_label(value: Any) -> str:
    text = clean_text(value)
    return SCENARIO_LABELS.get(text, text.replace("_", " ").title())


def shortlist_section_title(source_category: str) -> str:
    return SHORTLIST_SECTION_MAP.get(source_category, source_category)


def shortlist_source_category(section_title: str) -> str:
    for source, section in SHORTLIST_SECTION_MAP.items():
        if section == section_title:
            return source
    return section_title


def split_semicolon_text(value: Any) -> list[str]:
    text = clean_text(value, fallback="")
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def _join_phrases(parts: list[str]) -> str:
    items = [part for part in parts if part]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def derive_driver_list(row: pd.Series, top_n: int = 5) -> list[dict[str, Any]]:
    scores: dict[str, float] = {}

    def add(label: str, score: float) -> None:
        if not label or score <= 0:
            return
        scores[label] = max(scores.get(label, 0.0), score)

    reserve_pct = _num(row.get("peer_reserve_percentile"))
    margin_pct = _num(row.get("peer_margin_percentile"))
    leverage_pct = _num(row.get("peer_liability_percentile"))
    concentration_pct = _num(row.get("concentration_percentile"))
    reserve_gap = _num(row.get("reserve_gap_vs_peer_median"))
    leverage_gap = _num(row.get("leverage_gap_vs_peer_median"))
    margin_gap = _num(row.get("margin_gap_vs_peer_median"))
    revenue_hhi = _num(row.get("revenue_hhi_clean"))
    reserve_months = _num(row.get("reserve_months_proxy"))
    liability_ratio = _num(row.get("liability_ratio_clean"))
    net_asset_ratio = _num(row.get("net_asset_ratio_clean"))
    donation_share = _num(row.get("donation_share_clean"))
    revenue_growth = _num(row.get("revenue_growth_clean"))

    if reserve_pct is not None:
        if reserve_pct <= 0.10:
            add("peer-relative reserve weakness is severe", 5.0)
        elif reserve_pct <= 0.25:
            add("peer-relative reserves are below peers", 4.2)
        elif reserve_pct <= 0.40:
            add("reserve position trails peers", 2.8)

    if leverage_pct is not None:
        if leverage_pct >= 0.90:
            add("leverage is extreme versus peers", 4.8)
        elif leverage_pct >= 0.75:
            add("leverage sits above the peer threshold", 4.0)
        elif leverage_pct >= 0.60:
            add("balance-sheet leverage is elevated", 2.7)

    if margin_pct is not None:
        if margin_pct <= 0.15:
            add("margin is severely below peers", 4.4)
        elif margin_pct <= 0.25:
            add("margin trails peers", 3.6)
        elif margin_pct <= 0.40:
            add("operating performance is below peer median", 2.5)

    if concentration_pct is not None:
        if concentration_pct >= 0.90:
            add("revenue concentration is unusually high", 3.7)
        elif concentration_pct >= 0.75:
            add("revenue base is more concentrated than peers", 3.0)

    if reserve_months is not None and reserve_months <= 2.6:
        add("absolute reserve buffer is below the 2.6-month threshold", 3.9 + max(0.0, 2.6 - reserve_months) * 0.1)

    if liability_ratio is not None and liability_ratio >= 0.563:
        add("absolute leverage is above the retained threshold", 3.8 + min(liability_ratio - 0.563, 0.75))

    if net_asset_ratio is not None and net_asset_ratio <= 0.20:
        add("net asset cushion is thin", 2.8 + max(0.0, 0.20 - net_asset_ratio))

    if donation_share is not None and donation_share >= 0.65 and concentration_pct is not None and concentration_pct >= 0.75:
        add("donation exposure is concentrated", 3.1)

    if revenue_hhi is not None and revenue_hhi >= 0.985:
        add("revenue concentration crosses the 0.985 HHI threshold", 2.7)

    if revenue_growth is not None and revenue_growth < 0:
        add("revenue is contracting", 2.1 + min(abs(revenue_growth), 0.5))

    if reserve_gap is not None and reserve_gap <= -3:
        add("reserves are materially below the peer median", 3.4)

    if leverage_gap is not None and leverage_gap >= 0.20:
        add("liabilities run above the peer median", 3.0)

    if margin_gap is not None and margin_gap <= -0.05:
        add("margin is below the peer median", 2.6)

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_n]
    return [{"label": label, "score": round(score, 2)} for label, score in ranked]


def _parse_threshold_rule(rule: str) -> tuple[str, str, float] | None:
    match = re.match(r"([A-Za-z0-9_]+)\s*(<=|>=)\s*([-0-9.]+)", rule.strip())
    if not match:
        return None
    variable, operator, value = match.groups()
    return variable, operator, float(value)


def _row_metric_value(row: pd.Series, variable: str) -> float | None:
    if variable == "peer_pct_coverage_obs":
        return _num(row.get("peer_reserve_percentile"))
    if variable == "peer_pct_margin_obs":
        return _num(row.get("peer_margin_percentile"))
    return _num(row.get(variable))


def _threshold_specificity(segment: str, row: pd.Series) -> int:
    if segment == "overall":
        return 0
    if segment.startswith("size=") and clean_text(row.get("size_bucket"), fallback="") == segment.split("=", 1)[1]:
        return 2
    if segment.startswith("funding=") and clean_text(row.get("funding_bucket"), fallback="") == segment.split("=", 1)[1]:
        return 2
    return -1


def _threshold_label(variable: str, value: float) -> str:
    if variable == "reserve_months_proxy":
        return f"Reserve buffer below {value:.1f} months"
    if variable == "liability_ratio_clean":
        return f"Leverage above {value:.2f}x assets"
    if variable == "peer_pct_coverage_obs":
        return f"Peer reserve percentile in bottom {value * 100:.0f}%"
    if variable == "peer_pct_margin_obs":
        return f"Peer margin percentile in bottom {value * 100:.0f}%"
    if variable == "revenue_hhi_clean":
        return f"Revenue concentration above {value:.3f} HHI"
    return f"{variable} threshold triggered"


def derive_threshold_flags(row: pd.Series, threshold_scan: pd.DataFrame) -> list[dict[str, Any]]:
    if threshold_scan.empty:
        return []

    flags: list[dict[str, Any]] = []
    for variable in THRESHOLD_VARIABLES:
        variable_rows = threshold_scan.loc[threshold_scan["variable"] == variable].copy()
        if variable_rows.empty:
            continue

        variable_rows["specificity"] = variable_rows["segment"].astype(str).apply(lambda segment: _threshold_specificity(segment, row))
        variable_rows = variable_rows.loc[variable_rows["specificity"] >= 0].copy()
        if variable_rows.empty:
            continue

        variable_rows = variable_rows.sort_values(["specificity", "lift_or_odds_ratio"], ascending=[False, False])
        selected = variable_rows.iloc[0]
        parsed = _parse_threshold_rule(clean_text(selected.get("threshold_rule"), fallback=""))
        if parsed is None:
            continue
        _, operator, threshold_value = parsed
        current_value = _row_metric_value(row, variable)
        if current_value is None:
            continue

        triggered = current_value <= threshold_value if operator == "<=" else current_value >= threshold_value
        if not triggered:
            continue

        flags.append(
            {
                "label": _threshold_label(variable, threshold_value),
                "segment": clean_text(selected.get("segment"), fallback="overall"),
                "variable": variable,
                "threshold": threshold_value,
                "current_value": current_value,
                "lift": _num(selected.get("lift_or_odds_ratio")) or 0.0,
            }
        )

    return sorted(flags, key=lambda item: item["lift"], reverse=True)


def build_interpretation(row: pd.Series, drivers: list[dict[str, Any]], threshold_flags: list[dict[str, Any]]) -> str:
    bucket = clean_text(row.get("risk_bucket"), fallback="elevated")
    tone = {
        "Low": "low",
        "Watch": "watchlist-level",
        "High": "high",
        "Very High": "very high",
    }.get(bucket, bucket.lower())

    driver_labels = [driver["label"] for driver in drivers[:2]]
    if threshold_flags:
        threshold_phrase = threshold_flags[0]["label"].lower()
        if threshold_phrase not in " ".join(driver_labels):
            driver_labels.append(threshold_phrase)

    if driver_labels:
        return f"This organization is {tone} risk primarily because {_join_phrases(driver_labels[:3])}."

    peer_gap_text = clean_text(row.get("key_gaps"), fallback="no major peer weakness is exposed in the available artifacts")
    return f"This organization is {tone} risk, with the main visible weakness summarized as {peer_gap_text.lower()}."


def build_benchmark_table(row: pd.Series) -> pd.DataFrame:
    rows = []
    metrics = [
        ("Reserve buffer", "reserve_months_proxy", "reserve_gap_vs_peer_median", "peer_reserve_percentile", format_months),
        ("Operating margin", "operating_margin_clean", "margin_gap_vs_peer_median", "peer_margin_percentile", format_signed_percent),
        ("Leverage", "liability_ratio_clean", "leverage_gap_vs_peer_median", "peer_liability_percentile", format_ratio),
        ("Revenue concentration", "revenue_hhi_clean", "concentration_gap_vs_peer_median", "concentration_percentile", lambda value: format_ratio(value, digits=3, suffix="")),
    ]

    for label, value_col, gap_col, pct_col, formatter in metrics:
        value = _num(row.get(value_col))
        gap = _num(row.get(gap_col))
        pct = _num(row.get(pct_col))
        peer_median = value - gap if value is not None and gap is not None else None
        implication = "Relative strength"
        if label in {"Reserve buffer", "Operating margin"} and pct is not None and pct <= 0.35:
            implication = "Relative weakness"
        elif label in {"Leverage", "Revenue concentration"} and pct is not None and pct >= 0.65:
            implication = "Relative weakness"
        elif label in {"Leverage", "Revenue concentration"} and pct is not None and pct <= 0.35:
            implication = "Relative strength"
        elif label in {"Reserve buffer", "Operating margin"} and pct is not None and pct >= 0.65:
            implication = "Relative strength"

        rows.append(
            {
                "Metric": label,
                "Selected org": formatter(value),
                "Peer median": formatter(peer_median),
                "Percentile": format_percentile(pct),
                "Read": implication,
            }
        )

    return pd.DataFrame(rows)


def benchmark_callouts(row: pd.Series) -> tuple[str, str]:
    weakness_scores = {
        "Reserve position": 1 - (_num(row.get("peer_reserve_percentile")) or 0.5),
        "Margin position": 1 - (_num(row.get("peer_margin_percentile")) or 0.5),
        "Leverage position": _num(row.get("peer_liability_percentile")) or 0.5,
        "Concentration position": _num(row.get("concentration_percentile")) or 0.5,
    }
    strength_scores = {
        "Reserve position": _num(row.get("peer_reserve_percentile")) or 0.5,
        "Margin position": _num(row.get("peer_margin_percentile")) or 0.5,
        "Leverage position": 1 - (_num(row.get("peer_liability_percentile")) or 0.5),
        "Concentration position": 1 - (_num(row.get("concentration_percentile")) or 0.5),
    }

    strongest_weakness = max(weakness_scores.items(), key=lambda item: item[1])[0]
    strongest_strength = max(strength_scores.items(), key=lambda item: item[1])[0]

    weakness_text = {
        "Reserve position": "Relative weakness is concentrated in reserves.",
        "Margin position": "Relative weakness is concentrated in operating margin.",
        "Leverage position": "Relative weakness is concentrated in leverage.",
        "Concentration position": "Relative weakness is concentrated in revenue concentration.",
    }[strongest_weakness]

    strength_text = {
        "Reserve position": "Relative strength is reserve position.",
        "Margin position": "Relative strength is operating margin.",
        "Leverage position": "Relative strength is lower leverage.",
        "Concentration position": "Relative strength is revenue diversification.",
    }[strongest_strength]

    return weakness_text, strength_text


def peer_context_text(orgs: pd.DataFrame, row: pd.Series) -> str:
    if orgs.empty:
        return "Peer context is not available."

    size_slice = orgs.loc[orgs["size_bucket"] == row.get("size_bucket")]
    funding_slice = orgs.loc[orgs["funding_bucket"] == row.get("funding_bucket")]
    size_high = float(size_slice["risk_bucket"].isin(["High", "Very High"]).mean()) if not size_slice.empty else math.nan
    funding_med = float(funding_slice["predicted_distress_probability"].median()) if not funding_slice.empty else math.nan

    size_text = f"{size_high * 100:.0f}% of the {humanize_size_bucket(row.get('size_bucket'))} cohort screens High/Very High" if np.isfinite(size_high) else "size-band pressure is unavailable"
    funding_text = f"median baseline risk is {funding_med * 100:.1f}% for {humanize_funding_bucket(row.get('funding_bucket'))} organizations" if np.isfinite(funding_med) else "funding-model context is unavailable"
    return f"In peer context, {size_text}, and {funding_text}."


def shock_explanation(org_row: pd.Series, shock_row: pd.Series, source_mode: str) -> str:
    family = clean_text(shock_row.get("scenario_family"), fallback="")
    revenue_loss = _num(shock_row.get("shock_exposure_revenue_loss")) or 0.0
    expense_increase = _num(shock_row.get("shock_exposure_expense_increase")) or 0.0
    baseline_margin = _num(org_row.get("operating_margin_clean"))
    shocked_margin = _num(shock_row.get("operating_margin_clean"))
    baseline_reserve = _num(org_row.get("reserve_months_proxy"))
    shocked_reserve = _num(shock_row.get("reserve_months_proxy"))
    drivers = clean_text(shock_row.get("main_drivers"), fallback="no major driver change")

    if family == "expense_inflation":
        lead = f"The scenario adds roughly {format_currency_compact(expense_increase)} of expense pressure"
    elif family == "program_revenue":
        lead = f"The scenario removes roughly {format_currency_compact(revenue_loss)} of program revenue"
    elif family == "grant_government_revenue":
        lead = f"The scenario removes roughly {format_currency_compact(revenue_loss)} of grant / government revenue"
    else:
        lead = f"The scenario removes roughly {format_currency_compact(revenue_loss)} of donation-style revenue"

    detail_parts = []
    if baseline_margin is not None and shocked_margin is not None:
        detail_parts.append(f"margin moves from {format_signed_percent(baseline_margin)} to {format_signed_percent(shocked_margin)}")
    if baseline_reserve is not None and shocked_reserve is not None:
        detail_parts.append(f"reserve coverage shifts from {baseline_reserve:.1f} to {shocked_reserve:.1f} months")
    if drivers and drivers != "no major driver change":
        detail_parts.append(f"the main deterioration drivers are {drivers}")

    note = " This is a deterministic scenario engine, not a causal forecast."
    if source_mode == "fallback_packaged_org_level":
        note = " The org-level scenario row is a packaged fallback rather than an exact upgraded rerun." + note
    return lead + ", " + _join_phrases(detail_parts) + "." + note


def scenario_summary_table(org_shocks: pd.DataFrame) -> pd.DataFrame:
    if org_shocks.empty:
        return pd.DataFrame()
    table = org_shocks.copy()
    table["Scenario"] = table["scenario_name"].map(SCENARIO_LABELS).fillna(table["scenario_name"])
    table["Baseline risk"] = table["baseline_risk"].apply(format_probability)
    table["Shocked risk"] = table["shocked_risk"].apply(format_probability)
    table["Change"] = table["absolute_increase"].apply(format_points)
    table["Relative"] = table["relative_increase"].apply(format_relative)
    table["Transition"] = table["risk_bucket_transition"].fillna("No change")
    return table[["Scenario", "Baseline risk", "Shocked risk", "Change", "Relative", "Transition"]]


def most_sensitive_scenario(org_shocks: pd.DataFrame) -> pd.Series | None:
    if org_shocks.empty:
        return None
    return org_shocks.sort_values(["absolute_increase", "shocked_risk"], ascending=[False, False]).iloc[0]


def shortlist_table_for_section(shortlists: pd.DataFrame, section_title: str) -> pd.DataFrame:
    if shortlists.empty:
        return pd.DataFrame()
    source_category = shortlist_source_category(section_title)
    subset = shortlists.loc[shortlists["shortlist_category"] == source_category].copy()
    if subset.empty:
        return subset
    subset["Baseline risk"] = subset["predicted_distress_probability"].apply(format_probability)
    subset["Shock / resilience note"] = np.where(
        source_category == "Resilient outperformer",
        "Low baseline risk with strong reserve, margin, and leverage position",
        subset["shock_sensitivity_summary"].fillna(subset["worst_case_scenario"].map(SCENARIO_LABELS).fillna("Scenario note unavailable")),
    )
    subset["Rationale"] = subset["plain_english_recommendation"].fillna(subset["benchmark_position_summary"])
    return subset[
        [
            "business_name",
            "peer_group",
            "Baseline risk",
            "Shock / resilience note",
            "Rationale",
            "ein",
        ]
    ]
