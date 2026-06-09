"""
hub_spoke_model.py

This file calculates suitability for a hub-spoke logistics system.

Factors and weights (total = 100 pts):
  1. Multi-node Proximity     — 30 pts  (close to many terminals + parks = hub power)
  2. Logistics Park Quality   — 25 pts  (large, operational, multimodal parks)
  3. Terminal + Port Density  — 20 pts  (multiple IWAI terminals = freight base)
  4. Centrality / Connectivity— 15 pts  (rail + road + waterway access)
  5. Urban Market Access      — 10 pts  (large city = demand + labor)

Thresholds:
  >= 70  →  HIGH
  40-69  →  MEDIUM
  < 40   →  LOW
"""

MODEL_TYPE = "hub_spoke_logistics"

# 1. MULTI-NODE PROXIMITY
def _score_multi_node_proximity(sm, max_pts=30):
    """
    The more diverse node types in the region, the better the hub potential.
    Counts: terminals + logistics parks + urban centers (all in signals_by_type).
    """
    score = 0
    factors = []

    total_nodes = sm["terminal_count"] + sm["logistics_park_count"]

    # Count total infrastructure nodes (max 18)
    if total_nodes >= 5:
        node_pts = 18
    elif total_nodes >= 3:
        node_pts = 12
    elif total_nodes >= 2:
        node_pts = 7
    elif total_nodes == 1:
        node_pts = 3
    else:
        node_pts = 0
    score += node_pts
    factors.append(f"total_infra_nodes={total_nodes} → +{node_pts} pts")

    # Check diversity (both terminals and logistics parks)
    has_terminal = sm["terminal_count"] > 0
    has_park     = sm["logistics_park_count"] > 0
    if has_terminal and has_park:
        score += 8
        factors.append("both_terminals_and_parks → +8 pts (hub diversity)")
    elif has_terminal or has_park:
        score += 3
        factors.append("only_one_infra_type → +3 pts")
    else:
        factors.append("no_infra_nodes → +0 pts")

    # Check waterway connectivity
    if sm["any_waterway_lp"] == 1:
        score += 4
        factors.append("waterway_connected_park → +4 pts (trimodal hub)")

    return min(score, max_pts), factors


# 2. LOGISTICS PARK QUALITY
def _score_logistics_park_quality(sm, max_pts=25):
    """
    Large, operational logistics parks with good connectivity = strong hub base.
    """
    score = 0
    factors = []

    # Total area of logistics parks (max 10)
    area = sm["total_lp_area_acres"]
    if area >= 400:
        area_pts = 10
    elif area >= 200:
        area_pts = 7
    elif area >= 100:
        area_pts = 4
    elif area > 0:
        area_pts = 2
    else:
        area_pts = 0
    score += area_pts
    factors.append(f"total_lp_area={area} acres → +{area_pts} pts")

    # Status of logistics parks (max 8): Operational=8, Under Dev/Construction=5, Proposed=2
    status_pts = {3: 8, 2: 5, 1: 2, 0: 0}.get(sm["best_lp_status"], 0)
    score += status_pts
    factors.append(f"best_lp_status={sm['best_lp_status']} → +{status_pts} pts")

    # Number of logistics parks (max 7)
    count = sm["logistics_park_count"]
    count_pts = min(count * 2, 7)
    score += count_pts
    factors.append(f"logistics_park_count={count} → +{count_pts} pts")

    return min(score, max_pts), factors


# 3. TERMINAL DENSITY
def _score_terminal_density(sm, max_pts=20):
    """
    Terminal density and quality — the freight base of the hub.
    """
    score = 0
    factors = []

    # Total terminal capacity (max 10)
    cap = sm["total_capacity_mtpa"]
    if cap >= 5.0:
        cap_pts = 10
    elif cap >= 2.0:
        cap_pts = 7
    elif cap >= 0.5:
        cap_pts = 4
    elif cap > 0:
        cap_pts = 2
    else:
        cap_pts = 0
    score += cap_pts
    factors.append(f"total_terminal_capacity={cap}MTPA → +{cap_pts} pts")

    # Best terminal type (max 7): MMT=7, Fixed/IMT=5, Floating=2
    type_pts = {3: 7, 2: 5, 1: 2, 0: 0}.get(sm["best_terminal_type"], 0)
    score += type_pts
    factors.append(f"best_terminal_type={sm['best_terminal_type']} → +{type_pts} pts")

    # Rail connectivity (max 3)
    if sm["any_rail_terminal"] == 1:
        score += 3
        factors.append("rail_at_terminal → +3 pts (DFC connectivity)")

    return min(score, max_pts), factors


# 4. CONNECTIVITY (CENTRALITY)
def _score_centrality_connectivity(sm, max_pts=15):
    """
    Hub needs maximum modal connectivity: road + rail + waterway.
    """
    score = 0
    factors = []

    # Count distinct modal connections (road, rail, waterway, air)
    modals = 0
    modal_list = []

    # Check rail
    if sm["has_rail"] == 1:
        modals += 1
        modal_list.append("rail")
    # Check airport
    if sm["has_airport"] == 1:
        modals += 1
        modal_list.append("air")
    # Check waterway
    if sm["any_waterway_lp"] == 1 or sm["terminal_count"] > 0:
        modals += 1
        modal_list.append("waterway")
    # Road is assumed present at all locations (road always = 1 more)
    modals += 1
    modal_list.append("road")

    modal_pts = {4: 15, 3: 10, 2: 6, 1: 3}.get(modals, 0)
    score += modal_pts
    factors.append(f"modal_count={modals} ({'+'.join(modal_list)}) → +{modal_pts} pts")

    return min(score, max_pts), factors


# 5. URBAN MARKET
def _score_urban_market(sm, max_pts=10):
    """
    Proximity to large urban markets = demand for hub services.
    """
    score = 0
    factors = []

    pop = sm["total_population_lakhs"]
    if pop >= 30:
        pop_pts = 10
    elif pop >= 10:
        pop_pts = 7
    elif pop >= 3:
        pop_pts = 4
    elif pop >= 1:
        pop_pts = 2
    else:
        pop_pts = 1
    score += pop_pts
    factors.append(f"total_pop={pop}L → +{pop_pts} pts")

    return min(score, max_pts), factors


# CONSTRAINT CHECK
def _check_constraints(sm):
    constraints = []
    if sm["logistics_park_count"] == 0 and sm["terminal_count"] == 0:
        constraints.append("CRITICAL: No existing infra — full greenfield hub investment required")
    if sm["best_lp_status"] == 1 and sm["best_terminal_type"] <= 1:
        constraints.append("WARNING: Only proposed/floating infra — long lead time before hub viability")
    if sm["has_rail"] == 0 and sm["any_waterway_lp"] == 0:
        constraints.append("WARNING: No rail or waterway access — road-only hub has high logistics cost")
    if sm["total_lp_area_acres"] < 100 and sm["logistics_park_count"] > 0:
        constraints.append("NOTE: Small logistics park area — may need land acquisition for hub scale")
    return constraints


# MAIN FUNCTION
def score(entity):
    sm = entity["summary_metrics"]

    # Calculate scores
    mn_pts, mn_factors = _score_multi_node_proximity(sm)
    lq_pts, lq_factors = _score_logistics_park_quality(sm)
    td_pts, td_factors = _score_terminal_density(sm)
    cc_pts, cc_factors = _score_centrality_connectivity(sm)
    um_pts, um_factors = _score_urban_market(sm)

    total_score = mn_pts + lq_pts + td_pts + cc_pts + um_pts
    total_score = round(min(total_score, 100), 1)

    if total_score >= 70:
        level = "HIGH"
    elif total_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    factor_breakdown = {
        "multi_node_proximity":       {"score": mn_pts, "max": 30, "details": mn_factors},
        "logistics_park_quality":     {"score": lq_pts, "max": 25, "details": lq_factors},
        "terminal_density":           {"score": td_pts, "max": 20, "details": td_factors},
        "centrality_connectivity":    {"score": cc_pts, "max": 15, "details": cc_factors},
        "urban_market_access":        {"score": um_pts, "max": 10, "details": um_factors},
    }

    top_factor = max(factor_breakdown, key=lambda k: factor_breakdown[k]["score"])
    constraints = _check_constraints(sm)

    reasoning = (
        f"{entity['name']} scores {total_score}/100 for hub-spoke logistics suitability ({level}). "
        f"Strongest factor: {top_factor.replace('_',' ')} ({factor_breakdown[top_factor]['score']}/{factor_breakdown[top_factor]['max']} pts). "
        f"Infra nodes: {sm['terminal_count']} terminals + {sm['logistics_park_count']} logistics parks, "
        f"total lp area: {sm['total_lp_area_acres']} acres, modal count includes waterway: {sm['any_waterway_lp']}."
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
