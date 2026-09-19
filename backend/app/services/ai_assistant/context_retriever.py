"""Context Retriever for AI Disaster Assistant.

Fetches verified real-time database state and engine outputs to construct
grounded context for decision-support inquiries.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.entities import (
    HazardZone,
    Shelter,
    Population,
    RainfallRecord,
    EvacuationRoute,
    RelocationAssignment,
    Alert,
    Animal,
    AnimalShelter,
    CommunicationMessage,
    Hospital,
)


def retrieve_grounded_disaster_context(db: Session) -> Dict[str, Any]:
    """Queries active database models and compiles verified disaster state context."""
    # 1. Hazard Zones
    hz_list = db.query(HazardZone).all()
    red_zones = [h for h in hz_list if h.risk_level in ["RED", "CRITICAL", "HIGH"]]
    hazard_data = [
        {
            "id": h.id,
            "name": h.name,
            "hazard_type": h.hazard_type,
            "risk_level": h.risk_level,
            "risk_score": round(h.risk_score, 2),
        }
        for h in hz_list
    ]

    # 2. Shelters & Carrying Capacity
    shelters = db.query(Shelter).all()
    shelter_data = []
    total_cap = 0
    total_occ = 0
    overcrowded_shelters = []
    available_shelters = []

    for s in shelters:
        total_cap += s.capacity
        total_occ += s.current_occupancy
        avail = max(0, s.capacity - s.current_occupancy)
        s_info = {
            "id": s.id,
            "name": s.name,
            "capacity": s.capacity,
            "current_occupancy": s.current_occupancy,
            "available_capacity": avail,
            "occupancy_rate": round((s.current_occupancy / max(1, s.capacity)) * 100, 1),
            "safety_rating": s.structural_safety_rating,
            "contact": s.contact_number,
        }
        shelter_data.append(s_info)

        if avail > 0:
            available_shelters.append(s_info)
        if s_info["occupancy_rate"] >= 90.0:
            overcrowded_shelters.append(s_info)

    # 3. Population & Vulnerable Groups
    pop_records = db.query(Population).all()
    total_pop = sum(p.total_population for p in pop_records)
    vulnerable_pop = sum(p.vulnerable_population for p in pop_records)

    # 4. Rainfall Records
    rain_records = db.query(RainfallRecord).order_by(RainfallRecord.recorded_at.desc()).limit(5).all()
    rain_data = [
        {
            "location": r.location_name,
            "rainfall_mm": r.rainfall_mm,
            "duration_hours": r.duration_hours,
            "intensity": r.intensity,
        }
        for r in rain_records
    ]

    # 5. Evacuation Routes
    routes = db.query(EvacuationRoute).all()
    route_data = [
        {
            "id": r.id,
            "name": r.route_name,
            "distance_km": r.distance_km,
            "travel_time_mins": r.estimated_travel_time_mins,
            "is_safe": r.is_safe,
            "destination_shelter_id": r.destination_shelter_id,
        }
        for r in routes
    ]

    # 6. Active Alerts
    alerts = db.query(Alert).filter(Alert.status == "ACTIVE").all()
    alert_data = [
        {
            "id": a.id,
            "title": a.title,
            "severity": a.severity,
            "affected_area": a.affected_area,
            "recommended_action": a.recommended_action,
        }
        for a in alerts
    ]

    # 7. Animal Safety & Animal Shelters
    animals = db.query(Animal).all()
    at_risk_animals = [an for an in animals if an.emergency_status in ["AT_RISK", "EVACUATING"]]
    animal_shelters = db.query(AnimalShelter).all()
    animal_shelter_data = [
        {
            "id": ans.id,
            "name": ans.name,
            "capacity": ans.capacity,
            "occupancy": ans.current_occupancy,
            "available_capacity": ans.capacity - ans.current_occupancy,
            "types": ans.supported_animal_types,
        }
        for ans in animal_shelters
    ]

    # 8. Communication Broadcasts
    messages = db.query(CommunicationMessage).order_by(CommunicationMessage.created_at.desc()).limit(5).all()
    msg_data = [
        {
            "title": m.title,
            "category": m.category,
            "severity": m.severity,
            "target_area": m.target_area,
        }
        for m in messages
    ]

    # 9. Hospitals & Medical Capacity Data
    hospitals = db.query(Hospital).filter(Hospital.is_active == True).all()
    hospital_data = []
    total_hosp_beds = 0
    available_hosp_beds = 0
    total_icu_beds = 0
    available_icu_beds = 0
    total_em_beds = 0
    available_em_beds = 0
    total_ambulances_count = 0
    available_ambulances_count = 0

    open_hospitals = []
    full_hospitals = []

    for h in hospitals:
        cap = h.capacity
        av_b = max(0, cap.total_beds - cap.occupied_beds) if cap else 0
        av_i = max(0, cap.total_icu - cap.occupied_icu) if cap else 0
        av_e = max(0, cap.total_emergency_beds - cap.occupied_emergency_beds) if cap else 0
        av_a = cap.available_ambulances if cap else 0

        if cap:
            total_hosp_beds += cap.total_beds
            available_hosp_beds += av_b
            total_icu_beds += cap.total_icu
            available_icu_beds += av_i
            total_em_beds += cap.total_emergency_beds
            available_em_beds += av_e
            total_ambulances_count += cap.total_ambulances
            available_ambulances_count += av_a

        h_info = {
            "id": h.id,
            "hospital_id": h.hospital_id,
            "name": h.name,
            "type": h.type,
            "district": h.district,
            "address": h.address,
            "phone": h.phone,
            "emergency_status": h.emergency_status,
            "operational_status": h.operational_status,
            "specialization": h.specialization,
            "total_beds": cap.total_beds if cap else 0,
            "available_beds": av_b,
            "available_icu": av_i,
            "available_emergency_beds": av_e,
            "available_ambulances": av_a,
            "last_updated": cap.updated_at.isoformat() if cap and cap.updated_at else "Unavailable",
        }
        hospital_data.append(h_info)

        if h.operational_status == "OPEN":
            open_hospitals.append(h_info)
        elif h.operational_status == "FULL":
            full_hospitals.append(h_info)

    return {
        "hazard_zones": hazard_data,
        "red_zones_count": len(red_zones),
        "red_zone_names": [r["name"] for r in hazard_data if r["risk_level"] in ["RED", "CRITICAL", "HIGH"]],
        "shelters": shelter_data,
        "available_shelters": available_shelters,
        "overcrowded_shelters": overcrowded_shelters,
        "total_shelter_capacity": total_cap,
        "total_shelter_occupancy": total_occ,
        "available_total_capacity": max(0, total_cap - total_occ),
        "total_population": total_pop,
        "vulnerable_population": vulnerable_pop,
        "rainfall_records": rain_data,
        "routes": route_data,
        "active_alerts": alert_data,
        "animals_count": len(animals),
        "at_risk_animals_count": len(at_risk_animals),
        "animal_shelters": animal_shelter_data,
        "recent_broadcasts": msg_data,
        "hospitals": hospital_data,
        "total_hospitals_count": len(hospitals),
        "open_hospitals_count": len(open_hospitals),
        "full_hospitals_count": len(full_hospitals),
        "total_hospital_beds": total_hosp_beds,
        "available_hospital_beds": available_hosp_beds,
        "total_icu_beds": total_icu_beds,
        "available_icu_beds": available_icu_beds,
        "total_emergency_beds": total_em_beds,
        "available_emergency_beds": available_em_beds,
        "total_ambulances": total_ambulances_count,
        "available_ambulances": available_ambulances_count,
    }
