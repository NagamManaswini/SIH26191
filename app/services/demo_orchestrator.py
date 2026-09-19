import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.services.edge_manager import edge_simulation_manager

from app.schemas.demo import DemoStageInfo, DemoStatusResponse

class DemoOrchestrator:
    """
    Deterministic 15-Stage Flash Flood Scenario Engine for SIH Presentation.
    Coordinates real-time sensors, risk calculations, temporal AI forecasts,
    geo-fenced alert dispatch, hazard-avoidance evacuation, edge IoT nodes,
    local acoustic sirens, and backhaul outage / reconnection sync.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DemoOrchestrator, cls).__new__(cls)
            cls._instance._init_orchestrator()
        return cls._instance

    def _init_orchestrator(self):
        self.is_running: bool = False
        self.current_stage: int = 1
        self.auto_play: bool = False
        self.seconds_per_stage: int = 5
        self.last_action: str = "INITIALIZED"

        self.stages: Dict[int, DemoStageInfo] = {
            1: DemoStageInfo(
                stage_number=1,
                stage_title="Stage 1: Normal Baseline Conditions",
                stage_category="BASELINE",
                description="Catchment is in safe state. Clear atmospheric conditions, river within normal seasonal bounds, 0 active warnings.",
                system_effects=["All 48 IoT sensor nodes active", "Risk Engine: LOW (Score 12/100)", "No alerts active", "Shelters on standby"],
                rainfall_rate_mmh=2.4,
                river_water_level_m=1.20,
                soil_moisture_pct=34.0,
                risk_score=12.0,
                risk_level="LOW",
                predicted_level_m=1.25,
                active_alert_severity=None,
                evacuation_status="STANDBY",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            ),
            2: DemoStageInfo(
                stage_number=2,
                stage_title="Stage 2: Heavy Rainfall Begins",
                stage_category="METEOROLOGICAL_TRIGGER",
                description="Upper Himalayan cloudburst initiates heavy precipitation in Kedarnath glacial basin (45 mm/h).",
                system_effects=["Rainfall sensors detect rapid surge", "5-min moving rainfall increases 400%", "Telemetry broadcast via WebSocket"],
                rainfall_rate_mmh=48.5,
                river_water_level_m=1.35,
                soil_moisture_pct=46.0,
                risk_score=24.0,
                risk_level="LOW",
                predicted_level_m=1.60,
                active_alert_severity="INFO",
                evacuation_status="MONITORING",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            ),
            3: DemoStageInfo(
                stage_number=3,
                stage_title="Stage 3: Soil Moisture Saturation Increases",
                stage_category="CATCHMENT_SATURATION",
                description="Prolonged intense precipitation saturates steep mountain slopes (moisture rises to 76%). Infiltration capacity drops.",
                system_effects=["Runoff coefficient spikes to 0.88", "Soil moisture risk sub-score exceeds warning threshold", "Debris flow risk elevated"],
                rainfall_rate_mmh=62.0,
                river_water_level_m=1.85,
                soil_moisture_pct=76.0,
                risk_score=42.0,
                risk_level="MODERATE",
                predicted_level_m=2.40,
                active_alert_severity="ADVISORY",
                evacuation_status="PREPARATION",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            ),
            4: DemoStageInfo(
                stage_number=4,
                stage_title="Stage 4: River Water Level Begins Rising",
                stage_category="HYDROLOGICAL_RESPONSE",
                description="Mandakini river water gauge begins rapid vertical ascent at Gaurikund gorge (2.95 m, rate of rise +0.45 m/hr).",
                system_effects=["Radar gauge threshold approached", "Rate of rise score triggered", "Live Map reflects catchment color change"],
                rainfall_rate_mmh=74.0,
                river_water_level_m=2.95,
                soil_moisture_pct=84.0,
                risk_score=54.0,
                risk_level="HIGH",
                predicted_level_m=3.40,
                active_alert_severity="WATCH",
                evacuation_status="ALERT_STAGED",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            ),
            5: DemoStageInfo(
                stage_number=5,
                stage_title="Stage 5: Explainable Flood Risk Becomes HIGH",
                stage_category="RISK_ENGINE_ESCALATION",
                description="Weighted risk engine aggregates rainfall (74mm/h), soil saturation (84%), and river level (2.95m). Composite score reaches 68/100.",
                system_effects=["Explainable weighted risk breakdown updated", "Government officials notified", "Automated SMS/Push pipeline primed"],
                rainfall_rate_mmh=82.0,
                river_water_level_m=3.30,
                soil_moisture_pct=89.0,
                risk_score=68.0,
                risk_level="HIGH",
                predicted_level_m=3.95,
                active_alert_severity="WARNING",
                evacuation_status="READY_TO_DISPATCH",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            ),
            6: DemoStageInfo(
                stage_number=6,
                stage_title="Stage 6: AI Temporal Model Predicts Severe Surge",
                stage_category="AI_FORECASTING",
                description="Temporal AI model generates 30/60/90/120 min forecasts: river level predicted to breach 4.45 m danger mark within 60 minutes.",
                system_effects=["AI 60-min forecast: 4.45m (Confidence: 94%)", "Flood probability exceeds 88%", "Multi-horizon chart reflects upcoming peak"],
                rainfall_rate_mmh=94.0,
                river_water_level_m=3.65,
                soil_moisture_pct=92.0,
                risk_score=76.0,
                risk_level="CRITICAL",
                predicted_level_m=4.45,
                active_alert_severity="WARNING",
                evacuation_status="PRE_EVACUATION_ISSUED",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            ),
            7: DemoStageInfo(
                stage_number=7,
                stage_title="Stage 7: Watershed Risk Becomes CRITICAL",
                stage_category="CRITICAL_EVENT",
                description="Extreme combined surge: composite flood risk index escalates to 89/100. Catastrophic flash flood imminent.",
                system_effects=["DEFCON 1 Status activated on Command Center", "All sirens armed", "Emergency response units mobilized"],
                rainfall_rate_mmh=104.0,
                river_water_level_m=4.15,
                soil_moisture_pct=96.0,
                risk_score=89.0,
                risk_level="CRITICAL",
                predicted_level_m=4.80,
                active_alert_severity="EMERGENCY",
                evacuation_status="EVACUATE_IMMEDIATELY",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            ),
            8: DemoStageInfo(
                stage_number=8,
                stage_title="Stage 8: Geo-Fenced Alert Zone Generated",
                stage_category="MULTI_CHANNEL_DISPATCH",
                description="Automated Alert Engine computes 4.5 km circular geo-fenced danger polygon around Gaurikund-Kedarnath corridor.",
                system_effects=["Red Danger Zone rendered on GIS Map", "SMS/IVR/Push/Siren multi-channel dispatch fired", "NDRF units deployed"],
                rainfall_rate_mmh=108.0,
                river_water_level_m=4.40,
                soil_moisture_pct=97.0,
                risk_score=93.0,
                risk_level="CRITICAL",
                predicted_level_m=4.95,
                active_alert_severity="EMERGENCY",
                evacuation_status="ACTIVE_GEO_FENCE",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            ),
            9: DemoStageInfo(
                stage_number=9,
                stage_title="Stage 9: Hazard-Aware Safe Evacuation Activated",
                stage_category="EVACUATION_MANAGEMENT",
                description="Evacuation engine calculates safe ridge detour to Kedarnath Helipad Relief Sanctuary, avoiding flooded riverbanks.",
                system_effects=["Turn-by-turn safe ridge ascent directions computed", "Shelter bed availability verified (340 beds available)", "Cyan route polyline displayed"],
                rainfall_rate_mmh=112.0,
                river_water_level_m=4.55,
                soil_moisture_pct=98.0,
                risk_score=95.0,
                risk_level="CRITICAL",
                predicted_level_m=5.10,
                active_alert_severity="EMERGENCY",
                evacuation_status="HIGH_RIDGE_DETOUR_ACTIVE",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            ),
            10: DemoStageInfo(
                stage_number=10,
                stage_title="Stage 10: Edge LoRa Node Detects Local Surge",
                stage_category="EDGE_AUTONOMOUS_SENSING",
                description="Ground edge sensor node NODE-RN-001 at glacier basin samples extreme rainfall (115 mm/h) and river overflow.",
                system_effects=["Edge local algorithm computes risk 96/100", "Local threshold (70/100) breached on edge hardware", "Siren actuation circuit primed"],
                rainfall_rate_mmh=115.0,
                river_water_level_m=4.70,
                soil_moisture_pct=99.0,
                risk_score=96.0,
                risk_level="CRITICAL",
                predicted_level_m=5.15,
                active_alert_severity="EMERGENCY",
                evacuation_status="HIGH_RIDGE_DETOUR_ACTIVE",
                edge_siren_active=True,
                network_online=True,
                offline_buffer_count=0
            ),
            11: DemoStageInfo(
                stage_number=11,
                stage_title="Stage 11: Local Acoustic Siren Activates on Ground",
                stage_category="EDGE_ACTUATION",
                description="Autonomous edge acoustic siren sounds immediately on the valley floor to alert nearby residents and pilgrims.",
                system_effects=["Local acoustic siren sounding (110 dB)", "Flashing emergency strobe activated", "Zero-cloud-latency acoustic warning"],
                rainfall_rate_mmh=118.0,
                river_water_level_m=4.82,
                soil_moisture_pct=99.0,
                risk_score=97.0,
                risk_level="CRITICAL",
                predicted_level_m=5.20,
                active_alert_severity="EMERGENCY",
                evacuation_status="SIREN_ACTIVE_EVACUATING",
                edge_siren_active=True,
                network_online=True,
                offline_buffer_count=0
            ),
            12: DemoStageInfo(
                stage_number=12,
                stage_title="Stage 12: Cellular & Fiber Backhaul Network Failure",
                stage_category="RESILIENCY_TEST",
                description="Landslide tears transmission fiber; satellite link blocked by extreme cloudburst. Central cloud connectivity severed.",
                system_effects=["Backhaul network offline (Network Partition)", "Cloud server unable to reach edge nodes", "Nodes enter autonomous survival mode"],
                rainfall_rate_mmh=112.0,
                river_water_level_m=4.85,
                soil_moisture_pct=99.0,
                risk_score=97.0,
                risk_level="CRITICAL",
                predicted_level_m=5.20,
                active_alert_severity="EMERGENCY",
                evacuation_status="NETWORK_SEVERED_OFFLINE_SURVIVAL",
                edge_siren_active=True,
                network_online=False,
                offline_buffer_count=6
            ),
            13: DemoStageInfo(
                stage_number=13,
                stage_title="Stage 13: Local Edge Warning Continues Offline",
                stage_category="OFFLINE_SURVIVAL",
                description="Despite zero cellular / cloud connection, edge node continues sampling physical sensors, sounding siren, and caching telemetry in flash memory.",
                system_effects=["Autonomous local acoustic siren CONTINUES SOUNDING", "Edge telemetry packets queued in local non-volatile flash", "Community evacuation continues safely"],
                rainfall_rate_mmh=98.0,
                river_water_level_m=4.60,
                soil_moisture_pct=98.0,
                risk_score=92.0,
                risk_level="CRITICAL",
                predicted_level_m=4.90,
                active_alert_severity="EMERGENCY",
                evacuation_status="OFFLINE_WARNING_ACTIVE",
                edge_siren_active=True,
                network_online=False,
                offline_buffer_count=14
            ),
            14: DemoStageInfo(
                stage_number=14,
                stage_title="Stage 14: Cellular & Satellite Backhaul Restored",
                stage_category="RECOVERY",
                description="Emergency VSAT and secondary 4G tower restored by disaster telecommunications squad. Network link re-established.",
                system_effects=["Gateway backhaul online", "Central server discovers reconnected edge nodes", "Replay handshake initiated"],
                rainfall_rate_mmh=42.0,
                river_water_level_m=3.80,
                soil_moisture_pct=88.0,
                risk_score=64.0,
                risk_level="HIGH",
                predicted_level_m=3.50,
                active_alert_severity="WARNING",
                evacuation_status="RECOVERY_SYNCHRONIZING",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=14
            ),
            15: DemoStageInfo(
                stage_number=15,
                stage_title="Stage 15: Offline Events Synchronize to Cloud",
                stage_category="DATA_SYNCHRONIZATION",
                description="Edge sensor nodes flush their flash memory queues; all buffered telemetry frames and siren logs are committed to central database.",
                system_effects=["14 offline telemetry frames replayed and stored", "Full historical audit trail reconstructed", "Zero data loss achieved during disaster"],
                rainfall_rate_mmh=12.0,
                river_water_level_m=2.20,
                soil_moisture_pct=62.0,
                risk_score=34.0,
                risk_level="MODERATE",
                predicted_level_m=1.90,
                active_alert_severity="ADVISORY",
                evacuation_status="ALL_CLEAR_STABLE",
                edge_siren_active=False,
                network_online=True,
                offline_buffer_count=0
            )
        }

    def start_demo(self, auto_play: bool = True, seconds_per_stage: int = 5, jump_to_stage: Optional[int] = None) -> DemoStatusResponse:
        self.is_running = True
        self.auto_play = auto_play
        self.seconds_per_stage = seconds_per_stage
        self.current_stage = jump_to_stage if (jump_to_stage and 1 <= jump_to_stage <= 15) else 1
        self.last_action = f"STARTED_DEMO_STAGE_{self.current_stage}"

        # Synchronize edge simulator
        self._apply_stage_to_edge_simulator(self.current_stage)
        return self.get_status()

    def stop_demo(self) -> DemoStatusResponse:
        self.is_running = False
        self.auto_play = False
        self.current_stage = 1
        self.last_action = "STOPPED_RESET_TO_STAGE_1"

        # Reset edge simulator
        edge_simulation_manager.network_online = True
        for node in edge_simulation_manager.nodes.values():
            node.connected = True
            node.siren_status = False
            node.local_risk_score = 15.0
            node.stored_offline_events.clear()

        return self.get_status()

    def advance_stage(self, step: int = 1) -> DemoStatusResponse:
        if not self.is_running:
            self.is_running = True

        self.current_stage = min(15, max(1, self.current_stage + step))
        self.last_action = f"ADVANCED_TO_STAGE_{self.current_stage}"
        self._apply_stage_to_edge_simulator(self.current_stage)
        return self.get_status()

    def _apply_stage_to_edge_simulator(self, stage_num: int):
        stage = self.stages.get(stage_num)
        if not stage:
            return

        if stage_num in (12, 13):
            edge_simulation_manager.network_online = False
            for n in edge_simulation_manager.nodes.values():
                n.connected = False
                n.siren_status = True
                n.local_risk_score = stage.risk_score
                # Add buffered simulated events
                n.stored_offline_events = [{"evt": f"offline-sample-{i}"} for i in range(stage.offline_buffer_count // max(1, len(edge_simulation_manager.nodes)))]
        elif stage_num in (10, 11):
            edge_simulation_manager.network_online = True
            for n in edge_simulation_manager.nodes.values():
                n.connected = True
                n.siren_status = True
                n.local_risk_score = stage.risk_score
        elif stage_num in (14, 15):
            edge_simulation_manager.network_online = True
            for n in edge_simulation_manager.nodes.values():
                n.connected = True
                n.siren_status = False
                n.local_risk_score = stage.risk_score
                n.stored_offline_events.clear()
        else:
            edge_simulation_manager.network_online = True
            for n in edge_simulation_manager.nodes.values():
                n.connected = True
                n.siren_status = False
                n.local_risk_score = stage.risk_score
                n.stored_offline_events.clear()

    def get_status(self) -> DemoStatusResponse:
        current_info = self.stages.get(self.current_stage, self.stages[1])
        completed = list(range(1, self.current_stage))

        return DemoStatusResponse(
            is_running=self.is_running,
            current_stage=self.current_stage,
            total_stages=15,
            auto_play=self.auto_play,
            seconds_per_stage=self.seconds_per_stage,
            stage_info=current_info,
            active_watershed_name="Kedarnath Catchment (Mandakini Valley)",
            completed_stages=completed,
            last_action=self.last_action,
            message=f"Live Scenario: {current_info.stage_title}"
        )

# Singleton
demo_orchestrator = DemoOrchestrator()
