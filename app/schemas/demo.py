from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class DemoStageInfo(BaseModel):
    stage_number: int
    stage_title: str
    stage_category: str
    description: str
    system_effects: List[str]
    rainfall_rate_mmh: float
    river_water_level_m: float
    soil_moisture_pct: float
    risk_score: float
    risk_level: str
    predicted_level_m: float
    active_alert_severity: Optional[str] = None
    evacuation_status: str
    edge_siren_active: bool
    network_online: bool
    offline_buffer_count: int

class DemoStatusResponse(BaseModel):
    is_running: bool
    current_stage: int
    total_stages: int = 15
    auto_play: bool
    seconds_per_stage: int
    stage_info: DemoStageInfo
    active_watershed_name: str = "Kedarnath Catchment (Mandakini Valley)"
    completed_stages: List[int]
    last_action: str
    message: str

class DemoControlPayload(BaseModel):
    auto_play: bool = True
    seconds_per_stage: int = 4
    jump_to_stage: Optional[int] = None
