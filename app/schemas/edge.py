from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class LoRaGatewaySchema(BaseModel):
    gateway_id: str
    name: str
    latitude: float
    longitude: float
    elevation_m: float
    backhaul_type: str
    connected: bool
    packets_received: int
    packets_dropped: int
    packet_delivery_rate_pct: float
    last_uplink_at: str

class EdgeSensorNodeSchema(BaseModel):
    node_id: str
    name: str
    sensor_type: str
    latitude: float
    longitude: float
    elevation_m: float
    battery: float
    signal: float
    rssi_dbm: int
    snr_db: float
    frequency_mhz: float
    spreading_factor: int
    connected: bool
    gateway_id: str
    local_risk_score: float
    local_threshold: float
    siren_status: bool
    siren_reason: Optional[str] = None
    rainfall_rate_mmh: float
    river_level_m: float
    soil_moisture_pct: float
    offline_events_count: int
    last_sampled_at: str
    last_synced_at: Optional[str] = None

class EdgeSyncLogItem(BaseModel):
    sync_id: str
    node_id: str
    events_synced: int
    timestamp: str
    gateway_id: str
    status: str

class EdgeNetworkOverviewResponse(BaseModel):
    disclaimer: str
    network_online: bool
    total_nodes: int
    connected_nodes: int
    offline_nodes: int
    total_gateways: int
    sirens_active: int
    battery_low_nodes: int
    total_offline_queued_events: int
    gateways: List[LoRaGatewaySchema]
    nodes: List[EdgeSensorNodeSchema]
    recent_sync_logs: List[EdgeSyncLogItem]

class EdgeSimulationActionResponse(BaseModel):
    status: str
    message: str
    network_online: bool
    affected_nodes_count: Optional[int] = None
    total_events_synced: Optional[int] = None
    sync_timestamp: Optional[str] = None

class EdgeHazardTriggerResponse(BaseModel):
    status: str
    node_id: str
    network_online: bool
    siren_active: bool
    local_risk_score: float
    local_threshold: float
    siren_reason: Optional[str] = None
    stored_in_offline_buffer: bool
    current_offline_buffer_count: int
