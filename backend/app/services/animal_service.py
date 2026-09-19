"""Animal Safety Service.

Manages registered livestock & pets, animal shelters, and animal rescue plan generation
with strict capacity separation from human relief shelters.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.entities import Animal, AnimalShelter, AnimalRescueAssignment
from backend.app.schemas.animal import AnimalCreate, AnimalUpdate, AnimalShelterCreate


def get_all_animals(db: Session, emergency_status: Optional[str] = None, animal_type: Optional[str] = None) -> List[Animal]:
    """Retrieve all animals filtered by emergency status or type."""
    query = db.query(Animal)
    if emergency_status:
        query = query.filter(Animal.emergency_status == emergency_status.upper())
    if animal_type:
        query = query.filter(Animal.animal_type == animal_type.lower())
    return query.order_by(Animal.created_at.desc()).all()


def get_animal_by_id(db: Session, animal_id: int) -> Optional[Animal]:
    """Retrieve animal by primary key ID."""
    return db.query(Animal).filter(Animal.id == animal_id).first()


def create_animal(db: Session, animal_in: AnimalCreate) -> Animal:
    """Register a new animal or herd."""
    animal_obj = Animal(
        tag_id=animal_in.tag_id,
        owner_id=animal_in.owner_id,
        owner_name=animal_in.owner_name,
        animal_type=animal_in.animal_type.lower(),
        name=animal_in.name,
        location_name=animal_in.location_name,
        emergency_status=animal_in.emergency_status.upper(),
        rescue_status="PENDING",
    )
    db.add(animal_obj)
    db.commit()
    db.refresh(animal_obj)
    return animal_obj


def update_animal(db: Session, animal_id: int, animal_in: AnimalUpdate) -> Optional[Animal]:
    """Update emergency status, rescue status, or assigned shelter for an animal."""
    animal_obj = get_animal_by_id(db, animal_id)
    if not animal_obj:
        return None

    if animal_in.name is not None:
        animal_obj.name = animal_in.name
    if animal_in.location_name is not None:
        animal_obj.location_name = animal_in.location_name
    if animal_in.emergency_status is not None:
        animal_obj.emergency_status = animal_in.emergency_status.upper()
    if animal_in.rescue_status is not None:
        animal_obj.rescue_status = animal_in.rescue_status.upper()
    if animal_in.destination_shelter_id is not None:
        animal_obj.destination_shelter_id = animal_in.destination_shelter_id

    db.commit()
    db.refresh(animal_obj)
    return animal_obj


def get_animal_shelters(db: Session) -> List[Dict[str, Any]]:
    """Retrieve all animal shelters with calculated available capacity."""
    shelters = db.query(AnimalShelter).all()
    res = []
    for s in shelters:
        res.append({
            "id": s.id,
            "name": s.name,
            "address": s.address,
            "capacity": s.capacity,
            "current_occupancy": s.current_occupancy,
            "available_capacity": max(0, s.capacity - s.current_occupancy),
            "supported_animal_types": s.supported_animal_types,
            "water_availability": s.water_availability,
            "food_availability": s.food_availability,
            "safety_status": s.safety_status,
            "created_at": s.created_at,
        })
    return res


def create_animal_shelter(db: Session, shelter_in: AnimalShelterCreate) -> AnimalShelter:
    """Create a new dedicated animal shelter."""
    shelter_obj = AnimalShelter(
        name=shelter_in.name,
        address=shelter_in.address,
        capacity=shelter_in.capacity,
        current_occupancy=shelter_in.current_occupancy,
        supported_animal_types=shelter_in.supported_animal_types,
        water_availability=shelter_in.water_availability,
        food_availability=shelter_in.food_availability,
        safety_status=shelter_in.safety_status,
        location=shelter_in.location,
    )
    db.add(shelter_obj)
    db.commit()
    db.refresh(shelter_obj)
    return shelter_obj


def generate_animal_rescue_plan(db: Session) -> Dict[str, Any]:
    """Generates optimal animal rescue assignment to animal shelters without mixing human capacity."""
    at_risk_animals = db.query(Animal).filter(Animal.emergency_status.in_(["AT_RISK", "EVACUATING"])).all()
    animal_shelters = db.query(AnimalShelter).filter(AnimalShelter.safety_status == "SAFE").all()

    shelter_capacity_map = {s.id: max(0, s.capacity - s.current_occupancy) for s in animal_shelters}
    shelter_obj_map = {s.id: s for s in animal_shelters}

    assignments = []
    assigned_count = 0
    unassigned_count = 0

    for animal in at_risk_animals:
        assigned = False
        for s_id, avail_cap in shelter_capacity_map.items():
            if avail_cap > 0:
                s_obj = shelter_obj_map[s_id]
                supported = [t.strip().lower() for t in s_obj.supported_animal_types.split(",")]
                if animal.animal_type.lower() in supported or "other_livestock" in supported or "cattle" in supported:
                    # Assign animal to this shelter
                    animal.destination_shelter_id = s_id
                    animal.rescue_status = "IN_PROGRESS"
                    shelter_capacity_map[s_id] -= 1
                    s_obj.current_occupancy += 1

                    # Record assignment
                    rescue_assign = AnimalRescueAssignment(
                        animal_id=animal.id,
                        animal_shelter_id=s_id,
                        assigned_by="Animal Safety Optimizer",
                        status="ASSIGNED",
                    )
                    db.add(rescue_assign)

                    assignments.append({
                        "animal_id": animal.id,
                        "tag_id": animal.tag_id,
                        "animal_type": animal.animal_type,
                        "owner_name": animal.owner_name or "Community",
                        "assigned_shelter_id": s_id,
                        "assigned_shelter_name": s_obj.name,
                    })
                    assigned_count += 1
                    assigned = True
                    break

        if not assigned:
            animal.rescue_status = "UNASSIGNED"
            unassigned_count += 1

    db.commit()

    shelter_summary = [
        {
            "id": s.id,
            "name": s.name,
            "capacity": s.capacity,
            "current_occupancy": s.current_occupancy,
            "available_capacity": max(0, s.capacity - s.current_occupancy),
        }
        for s in animal_shelters
    ]

    return {
        "total_animals_at_risk": len(at_risk_animals),
        "total_animals_assigned": assigned_count,
        "total_unassigned": unassigned_count,
        "assignments": assignments,
        "animal_shelters_summary": shelter_summary,
    }
