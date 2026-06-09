"""
inland_port_model.py

This model calculates suitability for inland port development.

Factors and weights (total = 100 pts):
  1. River Stability          — 25 pts  (low flow variance, adequate depth)
  2. Terminal Proximity       — 25 pts  (existing IWAI terminal nearby)
  3. Logistics Park Access    — 20 pts  (MMLP/ICD within region)
  4. Water Quality            — 15 pts  (acceptable BOD/DO)
  5. Urban/Traffic Potential  — 15 pts  (city size + population)

Thresholds:
  >= 70  →  HIGH
  40–69  →  MEDIUM
  < 40   →  LOW

"""

MODEL_TYPE = "inland_port"

# 1. RIVER STABILITY
def _score_river_stability(sm, max_pts=25):
    """
    Rewards:
    - High flow_stability_code (1–4 scale → 4 = very stable)
    - Adequate navigability depth (>= 3m is ideal for large vessels)
    - Low flow_cv_proxy (monsoon/lean ratio; lower = more predictable)
    - Not flood prone
    """
    score = 0
    factors = []

    # Sub-factor A: flow stability (max 10 | higher is better)
    stab = sm["flow_stability_code"]  # 1–4
    stab_pts = round((stab / 4.0) * 10, 1)
    score += stab_pts
    factors.append(f"flow_stability={stab}/4 → +{stab_pts} pts")

    # Sub-factor B: navigability depth (max 10)
    depth = sm["nav_depth_m"]
    if depth >= 3.0:
        depth_pts = 10
    elif depth >= 2.5:
        depth_pts = 7
    elif depth >= 2.0:
        depth_pts = 4
    else:
        depth_pts = 1
    score += depth_pts
    factors.append(f"nav_depth={depth}m → +{depth_pts} pts")

    # Sub-factor C: flood penalty/condition (max 5)
    if sm["flood_prone"] == 0:
        flood_pts = 5
        factors.append("not_flood_prone → +5 pts")
    else:
        flood_pts = 0
        factors.append("flood_prone → +0 pts (penalty)")
    score += flood_pts

    return min(score, max_pts), factors


# 2. TERMINAL PROXIMITY
def _score_terminal_proximity(sm, max_pts=25):
  
    score = 0
    factors = []

    # Number of Terminals (max 10)
    count = sm["terminal_count"]
    if count >= 3:
        count_pts = 10
    elif count == 2:
        count_pts = 7
    elif count == 1:
        count_pts = 4
    else:
        count_pts = 0
    score += count_pts
    factors.append(f"terminal_count={count} → +{count_pts} pts")

    # Best terminal type: MMT=10, Fixed/IMT=7, Floating=4, None=0
    btype = sm["best_terminal_type"]
    type_pts = {3: 10, 2: 7, 1: 4, 0: 0}.get(btype, 0)
    score += type_pts
    factors.append(f"best_terminal_type={btype} → +{type_pts} pts")

    # Rail connectivity at terminal (max 5)
    if sm["any_rail_terminal"] == 1:
        score += 5
        factors.append("rail_connected_terminal → +5 pts")
    else:
        factors.append("no_rail_at_terminal → +0 pts")

    return min(score, max_pts), factors


# 3. LOGISTICS ACCESS
def _score_logistics_access(sm, max_pts=20):
    
    score = 0
    factors = []

    # Number of logistics parks (max 8)
    count = sm["logistics_park_count"]
    count_pts = min(count * 3, 8)
    score += count_pts
    factors.append(f"logistics_park_count={count} → +{count_pts} pts")

    # Status of best logistics park (max 8): Operational=8, Under Dev=5, Proposed=2, None=0
    status_pts = {3: 8, 2: 5, 1: 2, 0: 0}.get(sm["best_lp_status"], 0)
    score += status_pts
    factors.append(f"best_lp_status={sm['best_lp_status']} → +{status_pts} pts")

    # Waterway-connected park (max 4)
    if sm["any_waterway_lp"] == 1:
        score += 4
        factors.append("waterway_linked_logistics_park → +4 pts")

    return min(score, max_pts), factors


# 4. WATER QUALITY
def _score_water_quality(sm, max_pts=15):
   
    score = 0
    factors = []

    # BOD (max 8): lower is better. <3=8, 3-5=5, 5-8=2, >8=0
    bod = sm["avg_bod_mg_l"]
    if bod < 3.0:
        bod_pts = 8
    elif bod < 5.0:
        bod_pts = 5
    elif bod < 8.0:
        bod_pts = 2
    else:
        bod_pts = 0
    score += bod_pts
    factors.append(f"avg_BOD={bod}mg/L → +{bod_pts} pts")

    # DO (max 7): higher is better. >7=7, 6-7=5, 4-6=2, <4=0
    do_val = sm["avg_do_mg_l"]
    if do_val > 7.0:
        do_pts = 7
    elif do_val >= 6.0:
        do_pts = 5
    elif do_val >= 4.0:
        do_pts = 2
    else:
        do_pts = 0
    score += do_pts
    factors.append(f"avg_DO={do_val}mg/L → +{do_pts} pts")

    return min(score, max_pts), factors


# 5. TRAFFIC POTENTIAL
def _score_traffic_potential(sm, max_pts=15):
    """
    Rewards large nearby urban centers with good connectivity.
    """
    score = 0
    factors = []

    # City class (max 6)
    cc = sm["max_city_class"]   # 1–5
    cc_pts = round((cc / 5.0) * 6, 1)
    score += cc_pts
    factors.append(f"max_city_class={cc} → +{cc_pts} pts")

    # Population (max 5)
    pop = sm["total_population_lakhs"]
    if pop >= 20:
        pop_pts = 5
    elif pop >= 5:
        pop_pts = 3
    elif pop >= 1:
        pop_pts = 1
    else:
        pop_pts = 0
    score += pop_pts
    factors.append(f"total_pop={pop}L → +{pop_pts} pts")

    # Airport (max 2) and Rail (max 2)
    if sm["has_airport"]:
        score += 2
        factors.append("has_airport → +2 pts")
    if sm["has_rail"]:
        score += 2
        factors.append("has_rail_jn → +2 pts")

    return min(score, max_pts), factors


# CONSTRAINT CHECK
def _check_constraints(sm):
    """
    Hard constraints that can cap or flag a location regardless of score.
    Returns list of constraint strings.
    """
    constraints = []
    if sm["nav_depth_m"] < 1.5:
        constraints.append("CRITICAL: Nav depth < 1.5m — not navigable for commercial vessels")
    if sm["avg_bod_mg_l"] > 10.0:
        constraints.append("WARNING: BOD > 10 mg/L — severe water pollution, regulatory risk")
    if sm["flood_prone"] == 1 and sm["flow_stability_code"] < 2:
        constraints.append("WARNING: Flood-prone + low stability — high operational risk")
    if sm["env_sensitivity_code"] < 2:
        constraints.append("WARNING: High environmental sensitivity — NGT/clearance restrictions likely")
    if sm["terminal_count"] == 0 and sm["logistics_park_count"] == 0:
        constraints.append("NOTE: No existing terminals or logistics parks — greenfield investment required")
    return constraints


# ── Main scoring function ────────────────────────────────────────────────────
def score(entity):
    """
    Takes a location entity dict (from location_entity_builder).
    Returns a result dict matching the Phase 5 output structure.
    """
    sm = entity["summary_metrics"]

    rs_pts,  rs_factors  = _score_river_stability(sm)
    tp_pts,  tp_factors  = _score_terminal_proximity(sm)
    la_pts,  la_factors  = _score_logistics_access(sm)
    wq_pts,  wq_factors  = _score_water_quality(sm)
    tr_pts,  tr_factors  = _score_traffic_potential(sm)

    # Total score
    total_score = rs_pts + tp_pts + la_pts + wq_pts + tr_pts
    total_score = round(min(total_score, 100), 1)

    # Assign level
    if total_score >= 70:
        level = "HIGH"
    elif total_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Store factor breakdown
    factor_breakdown = {
        "river_stability":    {"score": rs_pts, "max": 25, "details": rs_factors},
        "terminal_proximity": {"score": tp_pts, "max": 25, "details": tp_factors},
        "logistics_access":   {"score": la_pts, "max": 20, "details": la_factors},
        "water_quality":      {"score": wq_pts, "max": 15, "details": wq_factors},
        "traffic_potential":  {"score": tr_pts, "max": 15, "details": tr_factors},
    }

    # Find strongest factor
    top_factor = max(factor_breakdown, key=lambda k: factor_breakdown[k]["score"])
    constraints = _check_constraints(sm)

    #Generate explanation
    reasoning = (
        f"{entity['name']} scores {total_score}/100 for inland port suitability ({level}). "
        f"Strongest factor: {top_factor.replace('_',' ')} ({factor_breakdown[top_factor]['score']}/{factor_breakdown[top_factor]['max']} pts). "
        f"River nav depth: {sm['nav_depth_m']}m, flow stability: {sm['flow_stability_code']}/4, "
        f"terminals in region: {sm['terminal_count']}, avg BOD: {sm['avg_bod_mg_l']} mg/L."
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
