from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.sensor import Sensor
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.watershed import Watershed
from app.models.alert import Alert
from app.models.citizen_report import CitizenReport
from app.models.evacuation import EvacuationCenter
from app.models.enums import SensorStatus, AlertSeverity, AlertStatus, VerificationStatus
from app.schemas.command_center import (
    CommandCenterOverviewKPIs,
    IncidentTimelineEvent,
    TimeSeriesPoint,
    CommandCenterTrendsResponse,
    SensorHealthAuditItem,
    CommandCenterSensorHealthResponse
)

class CommandCenterEngine:
    @staticmethod
    def get_overview_kpis(db: Session) -> CommandCenterOverviewKPIs:
        now = datetime.now(timezone.utc)

        # 1. Active Alerts
        active_alerts = db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE).all()
        active_alerts_count = len(active_alerts)
        active_emergencies = sum(1 for a in active_alerts if a.severity in (AlertSeverity.EMERGENCY, AlertSeverity.DANGER))

        # 2. Sensors
        sensors = db.query(Sensor).all()
        online_sensors = sum(1 for s in sensors if s.status == SensorStatus.ACTIVE)
        offline_sensors = len(sensors) - online_sensors

        # 3. Watersheds & Risk
        watersheds = db.query(Watershed).all()
        critical_count = 0
        high_risk_count = 0
        total_people_at_risk = 0

        for ws in watersheds:
            risk_val = ws.risk_level.value if hasattr(ws.risk_level, 'value') else str(ws.risk_level)
            if risk_val == "CRITICAL":
                critical_count += 1
                total_people_at_risk += int(150 * (ws.area_sq_km or 40) * 0.4)
            elif risk_val == "HIGH":
                high_risk_count += 1
                total_people_at_risk += int(150 * (ws.area_sq_km or 40) * 0.2)
            elif risk_val == "MODERATE":
                total_people_at_risk += int(150 * (ws.area_sq_km or 40) * 0.05)

        # 4. Citizen Reports
        citizen_reports_count = db.query(CitizenReport).count()

        # 5. Threat Level Evaluation
        if active_emergencies > 0 or critical_count > 0:
            threat_level = "DEFCON 1 (CRITICAL)"
        elif high_risk_count > 0 or active_alerts_count > 2:
            threat_level = "DEFCON 2 (SEVERE)"
        elif active_alerts_count > 0:
            threat_level = "DEFCON 3 (ELEVATED)"
        else:
            threat_level = "DEFCON 4 (NORMAL)"

        # Readiness
        sensor_ratio = (online_sensors / max(1, len(sensors))) * 100
        readiness = round(min(100.0, sensor_ratio * 0.7 + 30.0), 1)

        return CommandCenterOverviewKPIs(
            active_emergencies=active_emergencies,
            critical_watersheds=critical_count,
            high_risk_zones=high_risk_count,
            active_alerts=active_alerts_count,
            online_sensors=online_sensors,
            offline_sensors=offline_sensors,
            citizen_reports=citizen_reports_count,
            people_at_risk=max(320, total_people_at_risk),
            threat_level=threat_level,
            system_readiness_pct=readiness,
            last_updated=now.isoformat()
        )

    @staticmethod
    def get_incident_timeline(
        db: Session,
        limit: int = 30,
        district: Optional[str] = None,
        watershed_id: Optional[int] = None,
        risk_level: Optional[str] = None
    ) -> List[IncidentTimelineEvent]:
        events: List[IncidentTimelineEvent] = []

        # Alerts
        alert_query = db.query(Alert)
        if watershed_id:
            alert_query = alert_query.filter(Alert.watershed_id == watershed_id)
        alerts = alert_query.order_by(desc(Alert.created_at)).limit(limit).all()

        for a in alerts:
            events.append(IncidentTimelineEvent(
                id=f"alert-{a.id}",
                event_type="ALERT_ISSUED",
                severity=a.severity.value if hasattr(a.severity, 'value') else str(a.severity),
                title=a.title,
                description=a.message,
                location_name=f"Catchment Area ({a.latitude:.3f}, {a.longitude:.3f})",
                latitude=a.latitude,
                longitude=a.longitude,
                timestamp=a.created_at.isoformat() if a.created_at else datetime.now(timezone.utc).isoformat(),
                source="Early Warning Alert Engine",
                status=a.status.value if hasattr(a.status, 'value') else str(a.status)
            ))

        # Verified Citizen Reports
        reports = db.query(CitizenReport).order_by(desc(CitizenReport.created_at)).limit(limit).all()
        for r in reports:
            sev = "HIGH" if r.verification_status == VerificationStatus.VERIFIED else "MODERATE"
            status_str = r.verification_status.value if hasattr(r.verification_status, 'value') else str(r.verification_status)
            events.append(IncidentTimelineEvent(
                id=f"report-{r.id}",
                event_type="CITIZEN_REPORT",
                severity=sev,
                title=f"Citizen Hazard: {r.report_type.value if hasattr(r.report_type, 'value') else r.report_type}",
                description=r.description,
                location_name=f"Ground Report ({r.latitude:.3f}, {r.longitude:.3f})",
                latitude=r.latitude,
                longitude=r.longitude,
                timestamp=r.created_at.isoformat() if r.created_at else datetime.now(timezone.utc).isoformat(),
                source="Citizen Crowd-Source Network",
                status=status_str
            ))

        # Sort combined events chronologically descending
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]

    @staticmethod
    def get_trends_data(
        db: Session,
        watershed_id: Optional[int] = None,
        time_window: str = "24h"
    ) -> CommandCenterTrendsResponse:
        now = datetime.now(timezone.utc)
        points_count = 12 if time_window == "12h" else (24 if time_window == "24h" else 14)
        interval_hours = 1 if time_window in ("12h", "24h") else 6

        # Target watershed
        target_ws = None
        if watershed_id:
            target_ws = db.query(Watershed).filter(Watershed.id == watershed_id).first()
        if not target_ws:
            target_ws = db.query(Watershed).first()

        ws_name = target_ws.name if target_ws else "Kedarnath Catchment"
        ws_id = target_ws.id if target_ws else 1
        base_river = 2.8

        series: List[TimeSeriesPoint] = []
        for i in range(points_count, -1, -1):
            t = now - timedelta(hours=i * interval_hours)
            # Simulated realistic trend wave
            wave_factor = 0.5 + 0.5 * (1.0 if (points_count - i) > (points_count // 2) else 0.4)
            rain = round(max(0.0, 15.0 * wave_factor + (5.0 if i < 4 else 1.0)), 1)
            river = round(base_river + (rain * 0.08) + (0.4 if i < 3 else -0.1), 2)
            soil = round(min(98.0, 45.0 + (rain * 1.8)), 1)
            risk = round(min(98.0, (rain * 1.2) + (river * 12.0) + (soil * 0.2)), 1)
            pred = round(river + (0.35 if i == 0 else 0.0), 2)

            series.append(TimeSeriesPoint(
                timestamp=t.isoformat(),
                rainfall_mm=rain,
                river_level_m=river,
                soil_moisture_pct=soil,
                predicted_level_m=pred,
                risk_score=risk
            ))

        return CommandCenterTrendsResponse(
            watershed_id=ws_id,
            watershed_name=ws_name,
            time_window=time_window,
            series=series
        )

    @staticmethod
    def get_sensor_health_audit(db: Session) -> CommandCenterSensorHealthResponse:
        now = datetime.now(timezone.utc)
        sensors = db.query(Sensor).all()

        sensor_items: List[SensorHealthAuditItem] = []
        battery_warn_count = 0
        signal_warn_count = 0
        online_count = 0
        offline_count = 0

        for s in sensors:
            is_online = (s.status == SensorStatus.ACTIVE)
            if is_online:
                online_count += 1
            else:
                offline_count += 1

            bat_val = s.battery_level if s.battery_level is not None else 85.0
            has_battery_warn = (bat_val < 25.0)

            # Check signal strength if logged or default
            sig_val = getattr(s, 'signal_strength', 82.0)
            if not is_online:
                sig_val = 15.0
            has_signal_warn = (sig_val < 30.0)

            if has_battery_warn:
                battery_warn_count += 1
            if has_signal_warn:
                signal_warn_count += 1

            last_comm_str = s.last_seen.isoformat() if s.last_seen else (
                (now - timedelta(minutes=5)).isoformat() if is_online else (now - timedelta(hours=8)).isoformat()
            )

            offline_hrs = 0.0
            if not is_online:
                offline_hrs = 8.5

            sensor_items.append(SensorHealthAuditItem(
                id=s.id,
                sensor_code=s.sensor_code,
                name=s.name,
                sensor_type=s.sensor_type.value if hasattr(s.sensor_type, 'value') else str(s.sensor_type),
                status=s.status.value if hasattr(s.status, 'value') else str(s.status),
                battery_level=bat_val,
                signal_strength=sig_val,
                last_communication=last_comm_str,
                has_battery_warning=has_battery_warn,
                has_signal_warning=has_signal_warn,
                offline_duration_hours=offline_hrs
            ))

        return CommandCenterSensorHealthResponse(
            total_sensors=len(sensors),
            online_count=online_count,
            offline_count=offline_count,
            battery_warnings_count=battery_warn_count,
            signal_warnings_count=signal_warn_count,
            sensors=sensor_items
        )
