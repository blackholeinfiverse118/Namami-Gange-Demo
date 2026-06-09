"""
explanation_layer.py
===================================================
Takes scored results (from scoring_engine) and produces:
  1. A detailed human-readable explanation for each result
  2. A ranked factor analysis (what mattered most / least)
  3. An investment recommendation paragraph
  4. An enriched version of suitability_results.json with explanations
     saved to outputs/suitability_results_explained.json

Every result must answer (per the task spec):
  - Why HIGH / MEDIUM / LOW?
  - Which factors contributed most?
  - What constraints exist?


Usage:
  python src/explanation_layer.py
  → reads outputs/suitability_results.json
  → writes outputs/suitability_results_explained.json
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUTPUTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs"
)
INPUT_FILE  = os.path.join(OUTPUTS_DIR, "suitability_results.json")
OUTPUT_FILE = os.path.join(OUTPUTS_DIR, "suitability_results_explained.json")


# ── Factor importance labels ──
FACTOR_LABELS = {
    # inland_port
    "river_stability":    "River Stability",
    "terminal_proximity": "Proximity to Existing Terminals",
    "logistics_access":   "Logistics Park Access",
    "water_quality":      "Water Quality (BOD/DO)",
    "traffic_potential":  "Urban Traffic Potential",
    # seaplane
    "flow_turbulence":    "Flow Turbulence",
    "water_surface":      "Water Surface Adequacy",
    "traffic_density":    "Vessel Traffic Density",
    "urban_proximity":    "Urban Proximity & Demand",
    "env_clearance":      "Environmental Clearance",
    # hub_spoke
    "multi_node_proximity":    "Multi-Node Proximity",
    "logistics_park_quality":  "Logistics Park Quality",
    "terminal_density":        "Terminal & Port Density",
    "centrality_connectivity": "Centrality & Modal Connectivity",
    "urban_market_access":     "Urban Market Access",
}

MODEL_FULL_NAMES = {
    "inland_port":       "Inland Port Suitability",
    "seaplane_landing":  "Seaplane Landing Zone Suitability",
    "hub_spoke_logistics": "Hub-Spoke Logistics Hub Suitability",
}


# ── Core explanation builder ──
def build_explanation(result):
    """
    Builds a full explanation dict for a single scored result.
    Returns a dict to be merged into the result.
    """
    level  = result["suitability_level"]
    score  = result["score"]
    model  = result["model_type"]
    name   = result["location_name"]
    cf     = result["contributing_factors"]
    constraints = result["constraints"]

    # 1. Rank factors by score earned (descending) 
    ranked = sorted(
        cf.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )
    top_factor_key, top_factor_data   = ranked[0]
    bottom_factor_key, bottom_factor_data = ranked[-1]

    top_label    = FACTOR_LABELS.get(top_factor_key, top_factor_key)
    bottom_label = FACTOR_LABELS.get(bottom_factor_key, bottom_factor_key)
    model_label  = MODEL_FULL_NAMES.get(model, model)

    # 2. Why HIGH / MEDIUM / LOW? 
    if level == "HIGH":
        level_reason = (
            f"{name} qualifies as HIGH for {model_label} because it scored "
            f"{score}/100, clearing the 70-point threshold. "
            f"The dominant driver was '{top_label}' which contributed "
            f"{top_factor_data['score']}/{top_factor_data['max']} points. "
            f"This indicates strong real-world signal: existing infrastructure, "
            f"good river conditions, and adequate connectivity are all present."
        )
    elif level == "MEDIUM":
        level_reason = (
            f"{name} scores MEDIUM for {model_label} with {score}/100 "
            f"(between 40–69 points). "
            f"Strongest factor was '{top_label}' "
            f"({top_factor_data['score']}/{top_factor_data['max']} pts), "
            f"but '{bottom_label}' was a limiting factor "
            f"({bottom_factor_data['score']}/{bottom_factor_data['max']} pts). "
            f"The location has real potential but gaps in infrastructure "
            f"or river conditions prevent HIGH classification."
        )
    else:  # LOW
        level_reason = (
            f"{name} scores LOW for {model_label} with {score}/100 (below 40). "
            f"Even the strongest factor '{top_label}' only contributed "
            f"{top_factor_data['score']}/{top_factor_data['max']} pts. "
            f"The primary blockers are: "
            f"{'; '.join(constraints[:2]) if constraints else 'insufficient infrastructure and poor river conditions'}. "
            f"Significant investment or remediation would be required before "
            f"this location becomes viable."
        )

    # 3. Factor-by-factor narrative 
    factor_narratives = []
    for factor_key, factor_data in ranked:
        label     = FACTOR_LABELS.get(factor_key, factor_key)
        earned    = factor_data["score"]
        max_pts   = factor_data["max"]
        pct       = round((earned / max_pts) * 100) if max_pts > 0 else 0
        details   = factor_data.get("details", [])

        if pct >= 80:
            strength = "STRONG"
        elif pct >= 50:
            strength = "MODERATE"
        elif pct >= 25:
            strength = "WEAK"
        else:
            strength = "VERY WEAK"

        # Pick the single most impactful detail line
        key_detail = details[0] if details else "no detail available"

        factor_narratives.append({
            "factor":       label,
            "score_earned": earned,
            "score_max":    max_pts,
            "pct_of_max":   pct,
            "strength":     strength,
            "key_driver":   key_detail,
            "all_details":  details,
        })

    # 4. Constraints plain-English summary 
    if not constraints:
        constraint_summary = "No critical constraints identified. Location is suitable for immediate assessment."
    else:
        critical = [c for c in constraints if c.startswith("CRITICAL")]
        warnings = [c for c in constraints if c.startswith("WARNING")]
        notes    = [c for c in constraints if c.startswith("NOTE")]
        parts = []
        if critical:
            parts.append(f"{len(critical)} critical issue(s): {'; '.join(critical)}")
        if warnings:
            parts.append(f"{len(warnings)} warning(s): {'; '.join(warnings)}")
        if notes:
            parts.append(f"{len(notes)} note(s): {'; '.join(notes)}")
        constraint_summary = " | ".join(parts)

    # 5. Investment recommendation
    if level == "HIGH":
        recommendation = (
            f"RECOMMEND: {name} is a priority site for {model_label}. "
            f"Proceed with detailed project report (DPR) and site survey. "
            f"Key strength to leverage: {top_label}. "
            + (f"Address constraint: {constraints[0]}" if constraints else "No major blockers identified.")
        )
    elif level == "MEDIUM":
        recommendation = (
            f"CONDITIONAL: {name} requires targeted improvements before "
            f"{model_label} investment. "
            f"Focus on improving '{bottom_label}' "
            f"(currently {bottom_factor_data['score']}/{bottom_factor_data['max']} pts). "
            + (f"Key constraint to resolve: {constraints[0]}" if constraints else
               "No critical blockers — moderate investment will unlock HIGH potential.")
        )
    else:
        recommendation = (
            f"NOT RECOMMENDED at this time for {model_label} at {name}. "
            f"Score of {score}/100 indicates fundamental viability issues. "
            + (f"Primary blocker: {constraints[0]}" if constraints else
               "Core infrastructure and river conditions are inadequate.")
            + " Revisit after Namami Gange interventions or infra development."
        )

    return {
        "level_explanation":   level_reason,
        "factor_analysis":     factor_narratives,
        "constraint_summary":  constraint_summary,
        "recommendation":      recommendation,
        "top_factor":          top_label,
        "bottom_factor":       bottom_label,
        "top_factor_pct":      round((top_factor_data["score"] / top_factor_data["max"]) * 100),
        "bottom_factor_pct":   round((bottom_factor_data["score"] / bottom_factor_data["max"]) * 100),
    }


# Location-level summary across all 3 models
def build_location_summary(location_results):
    """
    Given the 3 model results for one location, produces a cross-model summary.
    """
    name   = location_results[0]["location_name"]
    scores = {r["model_type"]: r["score"] for r in location_results}
    levels = {r["model_type"]: r["suitability_level"] for r in location_results}

    best_model  = max(scores, key=scores.get)
    worst_model = min(scores, key=scores.get)

    level_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for lv in levels.values():
        level_counts[lv] += 1

    if level_counts["HIGH"] >= 2:
        overall = "PRIORITY SITE — HIGH potential across multiple use cases"
    elif level_counts["HIGH"] == 1:
        overall = f"SELECTIVE SITE — HIGH potential for {MODEL_FULL_NAMES.get(best_model, best_model)} only"
    elif level_counts["LOW"] >= 2:
        overall = "LOW PRIORITY — Not recommended for most infrastructure types"
    else:
        overall = "MODERATE SITE — Mixed signals; specific use-case investment possible"

    return {
        "location_name": name,
        "scores_by_model": scores,
        "levels_by_model": levels,
        "best_use_case":  MODEL_FULL_NAMES.get(best_model, best_model),
        "worst_use_case": MODEL_FULL_NAMES.get(worst_model, worst_model),
        "overall_assessment": overall,
    }


# Main enrichment function 
def enrich_results(input_path=INPUT_FILE, output_path=OUTPUT_FILE):
    """
    Reads suitability_results.json, enriches each result with full explanation,
    groups by location, adds location-level summaries, saves enriched JSON.
    """
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    # Support both GeoJSON FeatureCollection (new format) and flat JSON (legacy)
    # GeoJSON: data["features"][i]["properties"] contains the result
    # Flat:    data["results"][i] contains the result
    if data.get("type") == "FeatureCollection":
        results = [feature["properties"] for feature in data["features"]]
    else:
        results = data["results"]

    # Enrich each result
    enriched_results = []
    for r in results:
        explanation = build_explanation(r)
        enriched = {**r, "explanation": explanation}
        enriched_results.append(enriched)

    # Group by location for cross-model summary
    from collections import defaultdict
    by_location = defaultdict(list)
    for r in enriched_results:
        by_location[r["location_id"]].append(r)

    location_summaries = []
    for loc_id, loc_results in by_location.items():
        summary = build_location_summary(loc_results)
        summary["location_id"] = loc_id
        location_summaries.append(summary)

    # Sort summaries: PRIORITY SITE first
    location_summaries.sort(
        key=lambda x: -sum(x["scores_by_model"].values())
    )

    output = {
        "total_results":        len(enriched_results),
        "total_locations":      len(location_summaries),
        "location_summaries":   location_summaries,
        "results":              enriched_results,
    }

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[explanation_layer] Enriched {len(enriched_results)} results.")
    print(f"[explanation_layer] {len(location_summaries)} location summaries generated.")
    print(f"[explanation_layer] Saved → {output_path}\n")
    return output


def print_human_report(output):
    """Prints a readable per-location report to stdout."""
    print("\n" + "="*80)
    print("  GANGA BASIN SUITABILITY — FULL EXPLANATION REPORT")
    print("="*80)

    for summary in output["location_summaries"]:
        loc_id = summary["location_id"]
        print(f"\n{'─'*80}")
        print(f"  {summary['location_name']}  [{loc_id}]")
        print(f"   {summary['overall_assessment']}")
        print(f"   Best use:  {summary['best_use_case']}")
        print(f"   Scores:    ", end="")
        for model, score in summary["scores_by_model"].items():
            level_icon = {"HIGH": "[HIGH]", "MEDIUM": "[MEDIUM]", "LOW": "[LOW]"}.get(
                summary["levels_by_model"][model], ""
            )
            short = model.replace("_", " ").title()
            print(f"{short}: {score:.1f}{level_icon}  ", end="")
        print()

        # Print recommendation for the best model at this location
        best_model = max(summary["scores_by_model"], key=summary["scores_by_model"].get)
        for r in output["results"]:
            if r["location_id"] == loc_id and r["model_type"] == best_model:
                print(f"   → {r['explanation']['recommendation']}")
                if r["constraints"]:
                    print(f"   ⚠ Constraints: {r['explanation']['constraint_summary'][:120]}...")
                break

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    output = enrich_results()
    print_human_report(output)