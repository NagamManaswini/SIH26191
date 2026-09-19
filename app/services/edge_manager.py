import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class LoRaGateway:
    def __init__(self, gateway_id: str, name: str, latitude: float, longitude: float, elevation_m: float, backhaul_type: str):
        self.gateway_id = gateway_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.elevation_m = elevation_m
        self.backhaul_type = backhaul_type
        self.connected = True
        self.packets_received = 1500
        self.packets_dropped = 12
        self.packet_delivery_rate_pct = 99.2
        self.last_uplink_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gateway_id": self.gateway_id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "elevation_m": self.elevation_m,
            "backhaul_type": self.backhaul_type,
            "connected": self.connected,
            "packets_received": self.packets_received,
            "packets_dropped": self.packets_dropped,
            "packet_delivery_rate_pct": self.packet_delivery_rate_pct,
            "last_uplink_at": self.last_uplink_at,
        }

class EdgeSensorNode:
    def __init__(self, node_id: str, name: str, sensor_type: str, latitude: float, longitude: float, elevation_m: float, gateway_id: str):
        self.node_id = node_id
        self.name = name
        self.sensor_type = sensor_type
        self.latitude = latitude
        self.longitude = longitude
        self.elevation_m = elevation_m
        self.battery = 95.0
        self.signal = 88.0
        self.rssi_dbm = -75
        self.snr_db = 9.5
        self.frequency_mhz = 865.2
        self.spreading_factor = 7
        self.connected = True
        self.gateway_id = gateway_id
        self.local_risk_score = 15.0
        self.local_threshold = 70.0
        self.siren_status = False
        self.siren_reason = None
        self.rainfall_rate_mmh = 4.0
        self.river_level_m = 1.2
        self.soil_moisture_pct = 35.0
        self.offline_events_count = 0
        self.stored_offline_events = []
        self.last_sampled_at = datetime.now(timezone.utc).isoformat()
        self.last_synced_at = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "sensor_type": self.sensor_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "elevation_m": self.elevation_m,
            "battery": self.battery,
            "signal": self.signal,
            "rssi_dbm": self.rssi_dbm,
            "snr_db": self.snr_db,
            "frequency_mhz": self.frequency_mhz,
            "spreading_factor": self.spreading_factor,
            "connected": self.connected,
            "gateway_id": self.gateway_id,
            "local_risk_score": self.local_risk_score,
            "local_threshold": self.local_threshold,
            "siren_status": self.siren_status,
            "siren_reason": self.siren_reason,
            "rainfall_rate_mmh": self.rainfall_rate_mmh,
            "river_level_m": self.river_level_m,
            "soil_moisture_pct": self.soil_moisture_pct,
            "offline_events_count": len(self.stored_offline_events) if self.stored_offline_events else self.offline_events_count,
            "last_sampled_at": self.last_sampled_at,
            "last_synced_at": self.last_synced_at,
        }

class EdgeSimulationManager:
    def __init__(self):
        self.network_online: bool = True
        self.recent_sync_logs: List[Dict[str, Any]] = []
        self.gateways: Dict[str, LoRaGateway] = {
            "GW-KDR-001": LoRaGateway("GW-KDR-001", "Kedarnath Base Gateway", 30.7346, 79.0669, 3583.0, "Cellular 4G / Satellite"),
            "GW-GUR-002": LoRaGateway("GW-GUR-002", "Gaurikund Relay Gateway", 30.6480, 79.0270, 1982.0, "Fiber / Satellite"),
            "GW-SON-003": LoRaGateway("GW-SON-003", "Sonprayag Gateway", 30.6300, 78.9950, 1820.0, "Cellular 4G"),
        }
        self.nodes: Dict[str, EdgeSensorNode] = {
            "NODE-RN-001": EdgeSensorNode("NODE-RN-001", "Mandakini Upper Catchment Node", "Radar River & Acoustic Rain", 30.7100, 79.0500, 3200.0, "GW-KDR-001"),
            "NODE-RN-002": EdgeSensorNode("NODE-RN-002", "Rambara Gorge Node", "Ultrasonic Stream & Soil Gauge", 30.6800, 79.0400, 2590.0, "GW-GUR-002"),
            "NODE-RN-003": EdgeSensorNode("NODE-RN-003", "Gaurikund Confluence Node", "Optical River Gauge & Rain Tipping", 30.6500, 79.0300, 1980.0, "GW-GUR-002"),
            "NODE-RN-004": EdgeSensorNode("NODE-RN-004", "Sonprayag Bridge Node", "Hydrostatic Pressure & Radar Level", 30.6300, 78.9950, 1820.0, "GW-SON-003"),
            "NODE-RN-005": EdgeSensorNode("NODE-RN-005", "Kund Tributary Node", "Acoustic Rain & Soil Pore Pressure", 30.5800, 79.0100, 1650.0, "GW-SON-003"),
        }

    def get_overview(self) -> Dict[str, Any]:
        node_dicts = [node.to_dict() for node in self.nodes.values()]
        gw_dicts = [gw.to_dict() for gw in self.gateways.values()]
        connected_nodes = sum(1 for n in node_dicts if n["connected"])
        sirens_active = sum(1 for n in node_dicts if n["siren_status"])
        battery_low_nodes = sum(1 for n in node_dicts if n["battery"] < 20.0)
        total_offline_queued = sum(n["offline_events_count"] for n in node_dicts)

        return {
            "disclaimer": "SOFTWARE SIMULATION - Simulated LoRaWAN edge sensor nodes and local acoustic siren actuation engine.",
            "network_online": self.network_online,
            "total_nodes": len(node_dicts),
            "connected_nodes": connected_nodes if self.network_online else 0,
            "offline_nodes": len(node_dicts) - connected_nodes if self.network_online else len(node_dicts),
            "total_gateways": len(gw_dicts),
            "sirens_active": sirens_active,
            "battery_low_nodes": battery_low_nodes,
            "total_offline_queued_events": total_offline_queued,
            "gateways": gw_dicts,
            "nodes": node_dicts,
            "recent_sync_logs": self.recent_sync_logs[:10],
        }

    def simulate_network_failure(self) -> Dict[str, Any]:
        self.network_online = False
        for n in self.nodes.values():
            n.connected = False
        for gw in self.gateways.values():
            gw.connected = False
        return {
            "status": "SIMULATION_NETWORK_FAILED",
            "message": "Backhaul network disconnected. Edge sensor nodes operating in offline autonomous mode with local siren triggers.",
            "network_online": False,
            "affected_nodes_count": len(self.nodes)
        }

    def restore_network(self) -> Dict[str, Any]:
        self.network_online = True
        for n in self.nodes.values():
            n.connected = True
        for gw in self.gateways.values():
            gw.connected = True
        
        total_synced = 0
        sync_time = datetime.now(timezone.utc).isoformat()
        for n in self.nodes.values():
            events_cnt = len(n.stored_offline_events) or n.offline_events_count
            if events_cnt > 0:
                total_synced += events_cnt
                self.recent_sync_logs.insert(0, {
                    "sync_id": f"SYNC-{len(self.recent_sync_logs)+1:04d}",
                    "node_id": n.node_id,
                    "events_synced": events_cnt,
                    "timestamp": sync_time,
                    "gateway_id": n.gateway_id,
                    "status": "SYNCED_SUCCESS"
                })
                n.stored_offline_events = []
                n.offline_events_count = 0
                n.last_synced_at = sync_time
        
        if total_synced == 0:
            total_synced = 1
            self.recent_sync_logs.insert(0, {
                "sync_id": f"SYNC-{len(self.recent_sync_logs)+1:04d}",
                "node_id": "NODE-RN-001",
                "events_synced": 1,
                "timestamp": sync_time,
                "gateway_id": "GW-KDR-001",
                "status": "SYNCED_SUCCESS"
            })
        
        return {
            "status": "NETWORK_RESTORED",
            "message": "Backhaul connectivity restored. All queued telemetry packets successfully synchronized with cloud database.",
            "network_online": True,
            "total_events_synced": total_synced,
            "sync_timestamp": sync_time
        }

    def trigger_hazard_on_node(self, node_id: str) -> Dict[str, Any]:
        if node_id not in self.nodes:
            return {"error": f"Node {node_id} not found."}
        
        node = self.nodes[node_id]
        node.local_risk_score = 88.5
        node.siren_status = True
        node.siren_reason = f"CRITICAL: Local radar detected surge rate > safety threshold ({node.local_risk_score} >= {node.local_threshold})"
        node.river_level_m = 4.8
        node.rainfall_rate_mmh = 45.0
        
        stored = not self.network_online
        if stored:
            node.stored_offline_events.append({
                "evt_id": f"EVT-{len(node.stored_offline_events)+1}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "hazard": "FLASH_FLOOD_SURGE"
            })
            node.offline_events_count = len(node.stored_offline_events)
            
        return {
            "status": "HAZARD_TRIGGERED",
            "node_id": node.node_id,
            "network_online": self.network_online,
            "siren_active": node.siren_status,
            "local_risk_score": node.local_risk_score,
            "local_threshold": node.local_threshold,
            "siren_reason": node.siren_reason,
            "stored_in_offline_buffer": stored,
            "current_offline_buffer_count": len(node.stored_offline_events)
        }

    def sample_all_nodes(self) -> None:
        now_str = datetime.now(timezone.utc).isoformat()
        for n in self.nodes.values():
            n.last_sampled_at = now_str

edge_simulation_manager = EdgeSimulationManager()
