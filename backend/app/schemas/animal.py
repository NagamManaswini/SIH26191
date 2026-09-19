from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AnimalCreate(BaseModel):
    tag_id: str = Field(..., description="Unique tag or barcode ID for the animal or herd")
    owner_id: Optional[str] = Field(default=None, description="Owner citizen ID or community cooperative ID")
    owner_name: Optional[str] = Field(default=None, description="Owner full name")
    animal_type: str = Field(..., description="Animal category: cattle, goats, sheep, dogs, cats, poultry, other_livestock")
    name: Optional[str] = Field(default=None, description="Animal name or herd label")
    location_name: str = Field(default="Red Zone Alpha", description="Current location name")
    emergency_status: str = Field(default="AT_RISK", description="SAFE, AT_RISK, EVACUATING, RELOCATED")


class AnimalUpdate(BaseModel):
    name: Optional[str] = None
    location_name: Optional[str] = None
    emergency_status: Optional[str] = None
    rescue_status: Optional[str] = None
    destination_shelter_id: Optional[int] = None


class AnimalResponse(BaseModel):
    id: int
    tag_id: str
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    animal_type: str
    name: Optional[str] = None
    location_name: str
    emergency_status: str
    rescue_status: str
    destination_shelter_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnimalShelterCreate(BaseModel):
    name: str
    address: Optional[str] = None
    capacity: int = 200
    current_occupancy: int = 0
    supported_animal_types: str = "cattle,goats,sheep,dogs,cats,poultry,other_livestock"
    water_availability: bool = True
    food_availability: bool = True
    safety_status: str = "SAFE"
    location: str = "POINT(76.1350 11.5600)"


class AnimalShelterResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    capacity: int
    current_occupancy: int
    available_capacity: int
    supported_animal_types: str
    water_availability: bool
    food_availability: bool
    safety_status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RescuePlanResponse(BaseModel):
    total_animals_at_risk: int
    total_animals_assigned: int
    total_unassigned: int
    assignments: List[dict]
    animal_shelters_summary: List[dict]
