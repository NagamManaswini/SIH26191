"""Shelter Carrying Capacity & Suitability Assessment Engine."""

from typing import Dict, Any, List, Optional
import math
from sqlalchemy.orm import Session

from backend.app.models.entities import Shelter, ShelterResource, HazardZone
from backend.app.schemas.shelter import (
    ShelterCapacityMetricsResponse,
    ShelterEvaluateRequest,
    ShelterEvaluateResponse,
)
from backend.app.utils.geo import point_wkt_to_coords


def compute_resource_score(res: Optional[ShelterResource]) -> float:
    """Calculate resource score (0.0 to 1.0) based on water/food supply days, medical kits, power, sanitation."""
    if not res:
        return 0.2  # Base score if resources record is not present

    w_factor = min(1.0, float(res.water_supply_days) / 7.0)
    f_factor = min(1.0, float(res.food_supply_days) / 7.0)
    m_factor = min(1.0, float(res.medical_kits) / 50.0)
    p_factor = 1.0 if res.power_backup else 0.4
    s_factor = min(1.0, float(res.sanitation_facilities) / 20.0)

    score = 0.30 * w_factor + 0.30 * f_factor + 0.15 * m_factor + 0.15 * p_factor + 0.10 * s_factor
    return round(float(score), 4)


def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two lat/lon points."""
    R = 6371.0  # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(float(R * c), 2)


def evaluate_shelter_capacity(shelter: Shelter, db: Session) -> ShelterCapacityMetricsResponse:
    """Calculate carrying capacity, resource score, accessibility score, safety score, and overall suitability."""
    coords = point_wkt_to_coords(shelter.location)
    lat = coords[1] if coords else 0.0
    lon = coords[0] if coords else 0.0

    max_cap = int(shelter.capacity)
    curr_occ = int(shelter.current_occupancy)
    avail_cap = max(0, max_cap - curr_occ)
    occ_pct = round((curr_occ / max_cap) * 100.0 if max_cap > 0 else 100.0, 2)

    # Resource Score
    res_score = compute_resource_score(shelter.resources)

    # Accessibility Score (derived from rating)
    access_score = float(shelter.accessibility_rating) if shelter.accessibility_rating is not None else 0.8

    # Safety Score (derived from structural rating & hazard proximity)
    safety_score = float(shelter.structural_safety_rating) if shelter.structural_safety_rating is not None else 0.9

    # Can accept evacuees?
    can_accept = avail_cap > 0 and str(shelter.status).lower() == "active"

    # Overall Suitability score (0.0 to 1.0)
    if not can_accept:
        overall_suitability = 0.0
    else:
        cap_ratio = avail_cap / max_cap
        raw_suitability = (
            0.35 * cap_ratio
            + 0.25 * res_score
            + 0.20 * access_score
            + 0.20 * safety_score
        )
        overall_suitability = round(float(raw_suitability), 4)

    res_dict = {
        "water_supply_days": shelter.resources.water_supply_days if shelter.resources else 0.0,
        "food_supply_days": shelter.resources.food_supply_days if shelter.resources else 0.0,
        "medical_kits": shelter.resources.medical_kits if shelter.resources else 0,
        "power_backup": shelter.resources.power_backup if shelter.resources else False,
        "sanitation_facilities": shelter.resources.sanitation_facilities if shelter.resources else 0,
    }

    return ShelterCapacityMetricsResponse(
        id=shelter.id,
        name=shelter.name,
        maximum_capacity=max_cap,
        current_occupancy=curr_occ,
        available_capacity=avail_cap,
        occupancy_percentage=occ_pct,
        resource_score=res_score,
        accessibility_score=access_score,
        safety_score=safety_score,
        overall_suitability=overall_suitability,
        can_accept_evacuees=can_accept,
        status=shelter.status,
        latitude=lat,
        longitude=lon,
        resources_breakdown=res_dict,
    )


def evaluate_evacuee_assignment(
    req: ShelterEvaluateRequest, shelters: List[Shelter], db: Session
) -> ShelterEvaluateResponse:
    """Evaluate evacuee population assignment against available shelters."""
    evaluated_list: List[ShelterCapacityMetricsResponse] = []

    for s in shelters:
        metrics = evaluate_shelter_capacity(s, db)

        # Distance filter if origin is specified
        if req.origin_latitude is not None and req.origin_longitude is not None:
            dist = calculate_haversine_distance_km(
                req.origin_latitude, req.origin_longitude, metrics.latitude, metrics.longitude
            )
            if dist > req.max_distance_km:
                continue

        evaluated_list.append(metrics)

    # Sort shelters by overall suitability descending
    evaluated_list.sort(key=lambda x: x.overall_suitability, reverse=True)

    # Find first shelter that can accommodate the requested evacuee_count
    assigned_shelter = None
    for m in evaluated_list:
        if m.can_accept_evacuees and m.available_capacity >= req.evacuee_count:
            assigned_shelter = m
            break

    if assigned_shelter:
        return ShelterEvaluateResponse(
            evacuee_count=req.evacuee_count,
            assigned_shelter_id=assigned_shelter.id,
            assigned_shelter_name=assigned_shelter.name,
            is_assignment_possible=True,
            message=f"Optimal shelter '{assigned_shelter.name}' can safely accommodate {req.evacuee_count} evacuees.",
            suitable_shelters=evaluated_list,
        )
    else:
        return ShelterEvaluateResponse(
            evacuee_count=req.evacuee_count,
            assigned_shelter_id=None,
            assigned_shelter_name=None,
            is_assignment_possible=False,
            message=f"No single shelter has sufficient available capacity ({req.evacuee_count} required).",
            suitable_shelters=evaluated_list,
        )
