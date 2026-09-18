import pytest
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.models.enums import (
    UserRole, SensorType, SensorStatus, RiskLevel, AlertType, AlertSeverity,
    AlertStatus, CitizenReportType, VerificationStatus
)
from app.models.user import User
from app.models.watershed import Watershed
from app.models.sensor import Sensor
from app.models.readings import RainfallReading, RiverReading, SoilMoistureReading
from app.models.prediction import FloodPrediction
from app.models.alert import Alert
from app.models.citizen_report import CitizenReport
from app.models.evacuation import EvacuationCenter
from app.models.historical import HistoricalFloodEvent
from app.models.sensor_health import SensorHealth

def test_all_12_models_and_relationships():
    db = SessionLocal()
    try:
        # 1. User
        user = User(
            name="Test Observer",
            email=f"test.observer_{datetime.utcnow().timestamp()}@example.org",
            password_hash="hashed_pw_test",
            role=UserRole.RESEARCHER,
            district="Chamoli",
            state="Uttarakhand"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        assert user.id is not None
        assert user.role == UserRole.RESEARCHER

        # 2. Watershed
        ws = Watershed(
            name="Test Basin",
            code=f"WS-TEST-{int(datetime.utcnow().timestamp())}",
            district="Chamoli",
            state="Uttarakhand",
            area_sq_km=85.4,
            risk_level=RiskLevel.HIGH
        )
        db.add(ws)
        db.commit()
        db.refresh(ws)
        assert ws.id is not None

        # 3. Sensor
        sensor = Sensor(
            sensor_code=f"S-TEST-{int(datetime.utcnow().timestamp())}",
            name="Test River Radar",
            sensor_type=SensorType.RIVER_LEVEL,
            latitude=30.45,
            longitude=79.12,
            elevation=2100.0,
            watershed_id=ws.id,
            status=SensorStatus.ACTIVE,
            battery_level=95.0
        )
        db.add(sensor)
        db.commit()
        db.refresh(sensor)
        assert sensor.id is not None
        assert sensor.watershed.name == "Test Basin"

        # 4. Rainfall Reading
        rain = RainfallReading(
            sensor_id=sensor.id,
            rainfall_mm=18.5,
            timestamp=datetime.utcnow()
        )
        db.add(rain)

        # 5. River Reading
        river = RiverReading(
            sensor_id=sensor.id,
            water_level_m=3.4,
            flow_rate=120.5,
            timestamp=datetime.utcnow()
        )
        db.add(river)

        # 6. Soil Moisture Reading
        soil = SoilMoistureReading(
            sensor_id=sensor.id,
            moisture_percentage=78.2,
            timestamp=datetime.utcnow()
        )
        db.add(soil)

        # 7. Flood Prediction
        pred = FloodPrediction(
            watershed_id=ws.id,
            prediction_time=datetime.utcnow(),
            forecast_for=datetime.utcnow() + timedelta(minutes=60),
            predicted_water_level=4.2,
            probability=76.0,
            risk_level=RiskLevel.HIGH,
            confidence=89.5,
            model_version="v1.0-temporal"
        )
        db.add(pred)

        # 8. Alert
        alert = Alert(
            alert_type=AlertType.FLASH_FLOOD,
            severity=AlertSeverity.WARNING,
            title="Test High Water Alert",
            message="Rapid water level rise detected.",
            latitude=30.45,
            longitude=79.12,
            radius_km=5.0,
            status=AlertStatus.ACTIVE
        )
        db.add(alert)

        # 9. Citizen Report
        report = CitizenReport(
            user_id=user.id,
            report_type=CitizenReportType.WATER_OVERFLOW,
            description="Culvert overflowing near bridge.",
            latitude=30.45,
            longitude=79.12,
            verification_status=VerificationStatus.PENDING
        )
        db.add(report)

        # 10. Evacuation Center
        center = EvacuationCenter(
            name="Test Relief Hub",
            latitude=30.45,
            longitude=79.12,
            capacity=300,
            current_occupancy=25,
            contact_number="+91-0000000000",
            facilities="Medical, Food"
        )
        db.add(center)

        # 11. Historical Flood Event
        hist = HistoricalFloodEvent(
            name="Test Historical Cloudburst",
            location="Test Valley",
            start_time=datetime(2022, 7, 10, 10, 0, 0),
            end_time=datetime(2022, 7, 10, 18, 0, 0),
            maximum_rainfall=180.0,
            maximum_water_level=5.6,
            affected_area="25 sq km",
            severity=RiskLevel.HIGH
        )
        db.add(hist)

        # 12. Sensor Health Log
        health = SensorHealth(
            sensor_id=sensor.id,
            battery_level=95.0,
            signal_strength=-72.0,
            status=SensorStatus.ACTIVE,
            recorded_at=datetime.utcnow()
        )
        db.add(health)

        db.commit()

        # Verify relationships
        db.refresh(sensor)
        assert len(sensor.rainfall_readings) >= 1
        assert len(sensor.river_readings) >= 1
        assert len(sensor.soil_moisture_readings) >= 1
        assert len(sensor.health_logs) >= 1

        db.refresh(ws)
        assert len(ws.predictions) >= 1
        assert len(ws.sensors) >= 1

        db.refresh(user)
        assert len(user.citizen_reports) >= 1

    finally:
        db.close()
