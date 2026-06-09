"""
seaplane_model.py

This file calculates suitability for seaplane landing zones.

Factors and weights (total = 100 pts):
  1. Low Flow Turbulence      — 25 pts  (calm water needed for safe landing)
  2. Water Surface Adequacy   — 20 pts  (sufficient stretch, low turbidity)
  3. Low Traffic Density      — 20 pts  (few large vessels / barge traffic)
  4. Urban Proximity          — 20 pts  (tourism/demand driver)
  5. Environmental Clearance  — 15 pts  (no restrictions: dolphin zones, protected areas)

Thresholds:
  >= 70  →  HIGH
  40–69  →  MEDIUM
  < 40   →  LOW
"""

MODEL_TYPE = "seaplane_landing"

# 1. FLOW TURBULENCE
def _score_flow_turbulence(sm, max_pts=25):
    """
    Seaplanes need calm, predictable water surfaces.
    High CV proxy = turbulent = bad. High stability = good.
    """
    score = 0
    factors = []

    # Flow stability (max 12): stable river = good landing surface(higher is better)
    stab = sm["flow_stability_code"]  # 1-4
    stab_pts = round((stab / 4.0) * 12, 1)
    score += stab_pts
    factors.append(f"flow_stability={stab}/4 → +{stab_pts} pts")

    # Flow CV proxy (max 8): lower monsoon/lean ratio = less turbulence swing(lower is better)
    cv = sm["flow_cv_proxy"]
    if cv < 20:
        cv_pts = 8    # very stable year-round
    elif cv < 50:
        cv_pts = 5
    elif cv < 100:
        cv_pts = 2
    else:
        cv_pts = 0    # extremely turbulent in monsoon
    score += cv_pts
    factors.append(f"flow_cv_proxy={cv} (monsoon/lean ratio) → +{cv_pts} pts")

    # Water level variation (max 5): smaller variation = calmer surface
    wlv = sm.get("water_level_var_m", sm.get("nav_depth_m", 10.0))
    # Use a proxy: if nav_depth >= 2.5m (deep enough but not flood) = good
    depth = sm["nav_depth_m"]
    if 2.0 <= depth <= 4.0:
        wlv_pts = 5   # ideal depth range for seaplanes
    elif depth > 4.0:
        wlv_pts = 3   # deep but could have tidal/ship traffic
    else:
        wlv_pts = 1
    score += wlv_pts
    factors.append(f"nav_depth={depth}m (seaplane runway depth) → +{wlv_pts} pts")

    return min(score, max_pts), factors


# 2. WATER SURFACE QUALITY
def _score_water_surface(sm, max_pts=20):
    """
    Need sufficient calm water surface: low turbidity, acceptable quality.
    Tidal zones (Haldia, Kolkata) have turbidity issues.
    """
    score = 0
    factors = []

    # Turbidity (max 12): lower is better for visibility / surface quality
    turb = sm["avg_turbidity_ntu"]
    if turb < 20:
        turb_pts = 12
    elif turb < 50:
        turb_pts = 8
    elif turb < 100:
        turb_pts = 4
    else:
        turb_pts = 0
    score += turb_pts
    factors.append(f"avg_turbidity={turb} NTU → +{turb_pts} pts")

    # Water quality class (max 8): clean water = better visibility
    wq = sm["avg_wq_class_code"]  # 1-5, 5=best
    wq_pts = round((wq / 5.0) * 8, 1)
    score += wq_pts
    factors.append(f"avg_wq_class={wq}/5 → +{wq_pts} pts")

    return min(score, max_pts), factors


# 3. TRAFFIC DENSITY
def _score_traffic_density(sm, max_pts=20):
    """
    Fewer large terminals and commercial ports = less vessel traffic = safer for seaplanes.
    Seaplanes need clear water stretches.
    """
    score = 0
    factors = []

    # Penalise heavy commercial traffic (many large terminals = congested water)
    term_count = sm["terminal_count"]
    cap = sm["total_capacity_mtpa"]

    # Less traffic is better for seaplanes
    if cap == 0 and term_count == 0:
        traffic_pts = 20   # no commercial traffic at all
        factors.append("no_commercial_terminals → +20 pts (clear water)")
    elif cap < 0.5:
        traffic_pts = 15
        factors.append(f"low_terminal_capacity={cap}MTPA → +15 pts")
    elif cap < 2.0:
        traffic_pts = 10
        factors.append(f"medium_terminal_capacity={cap}MTPA → +10 pts")
    elif cap < 5.0:
        traffic_pts = 5
        factors.append(f"high_terminal_capacity={cap}MTPA → +5 pts (busy water)")
    else:
        traffic_pts = 0
        factors.append(f"very_high_capacity={cap}MTPA → +0 pts (heavily congested)")
    score += traffic_pts

    return min(score, max_pts), factors


# 4. URBAN PROXIMITY
def _score_urban_proximity(sm, max_pts=20):
    """
    Seaplanes need tourism/business demand: large cities, airports, accessibility.
    """
    score = 0
    factors = []

    # City class (max 8)
    cc = sm["max_city_class"]
    cc_pts = round((cc / 5.0) * 8, 1)
    score += cc_pts
    factors.append(f"max_city_class={cc} → +{cc_pts} pts")

    # Population (max 6)
    pop = sm["total_population_lakhs"]
    if pop >= 10:
        pop_pts = 6
    elif pop >= 3:
        pop_pts = 4
    elif pop >= 1:
        pop_pts = 2
    else:
        pop_pts = 0
    score += pop_pts
    factors.append(f"total_pop={pop}L → +{pop_pts} pts")

    # Airport presence nearby (max 4) — existing air travel demand = seaplane demand
    if sm["has_airport"]:
        score += 4
        factors.append("existing_airport → +4 pts (air travel demand)")
    else:
        factors.append("no_airport → +0 pts")

    # Railway connectivity(max 2) — multimodal access
    if sm["has_rail"]:
        score += 2
        factors.append("has_rail_jn → +2 pts")

    return min(score, max_pts), factors


# 5. ENVIRONMENTAL CLEARANCE
def _score_env_clearance(sm, max_pts=15):
    """
    Environmental sensitivity reduces score.
    Protected zones, dolphin habitats, high env sensitivity = restrictions.
    """
    score = 0
    factors = []

    # Env sensitivity code (1=high sensitivity/restrictions, 3=low=clear)
    env = sm["env_sensitivity_code"]  # 1–3
    env_pts = round((env / 3.0) * 12, 1)
    score += env_pts
    label = {1: "HIGH (likely restricted)", 2: "MEDIUM (check NGT)", 3: "LOW (clear)"}.get(round(env), "MEDIUM")
    factors.append(f"env_sensitivity={env}/3 ({label}) → +{env_pts} pts")

    # Flood prone is also an env/safety risk for seaplanes
    if sm["flood_prone"] == 0:
        score += 3
        factors.append("not_flood_prone → +3 pts (safe operations)")
    else:
        factors.append("flood_prone → +0 pts (seasonal closure risk)")

    return min(score, max_pts), factors


# CONSTRAINT CHECK
def _check_constraints(sm):
    constraints = []
    if sm["avg_turbidity_ntu"] > 150:
        constraints.append("CRITICAL: Turbidity > 150 NTU — poor visibility for seaplane landing")
    if sm["flow_stability_code"] < 2:
        constraints.append("CRITICAL: Very unstable flow — unsafe water surface for aircraft")
    if sm["env_sensitivity_code"] < 1.5:
        constraints.append("CRITICAL: High environmental sensitivity zone — NGT/wildlife clearance required")
    if sm["total_capacity_mtpa"] > 5.0:
        constraints.append("WARNING: Heavy commercial port traffic — water zone coordination required")
    if sm["nav_depth_m"] < 1.5:
        constraints.append("WARNING: Shallow water may restrict seaplane hull draft")
    return constraints


# MAIN FUNCTION
def score(entity):
    sm = entity["summary_metrics"]

    # Calculate all scores
    ft_pts, ft_factors = _score_flow_turbulence(sm)
    ws_pts, ws_factors = _score_water_surface(sm)
    td_pts, td_factors = _score_traffic_density(sm)
    up_pts, up_factors = _score_urban_proximity(sm)
    ec_pts, ec_factors = _score_env_clearance(sm)

    # Total score
    total_score = ft_pts + ws_pts + td_pts + up_pts + ec_pts
    total_score = round(min(total_score, 100), 1)

    # Assign level
    if total_score >= 70:
        level = "HIGH"
    elif total_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Store breakdown
    factor_breakdown = {
        "flow_turbulence":    {"score": ft_pts, "max": 25, "details": ft_factors},
        "water_surface":      {"score": ws_pts, "max": 20, "details": ws_factors},
        "traffic_density":    {"score": td_pts, "max": 20, "details": td_factors},
        "urban_proximity":    {"score": up_pts, "max": 20, "details": up_factors},
        "env_clearance":      {"score": ec_pts, "max": 15, "details": ec_factors},
    }

    # Find best factor
    top_factor = max(factor_breakdown, key=lambda k: factor_breakdown[k]["score"])
    constraints = _check_constraints(sm)

    # Explanation
    reasoning = (
        f"{entity['name']} scores {total_score}/100 for seaplane landing suitability ({level}). "
        f"Strongest factor: {top_factor.replace('_',' ')} ({factor_breakdown[top_factor]['score']}/{factor_breakdown[top_factor]['max']} pts). "
        f"Flow stability: {sm['flow_stability_code']}/4, turbidity: {sm['avg_turbidity_ntu']} NTU, "
        f"env sensitivity: {sm['env_sensitivity_code']}/3, commercial capacity in zone: {sm['total_capacity_mtpa']} MTPA."
    )

    return {
        "location_id":         entity["entity_id"],
        "latitude":            entity["latitude"],
        "longitude":           entity["longitude"],
        "model_type":          MODEL_TYPE,
        "suitability_level":   level,
        "score":               total_score,
        "contributing_factors": factor_breakdown,
        "constraints":         constraints,
        "reasoning":           reasoning,
    }
