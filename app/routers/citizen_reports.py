"""
Citizen Crowd-Sourcing Router for Real-Time Ground Reports.

Provides endpoints for submitting geo-tagged disaster reports,
retrieving sensor-corroborated reports, and role-protected verification.
"""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.citizen_report import CitizenReport
from app.models.user import User
from app.models.enums import UserRole, VerificationStatus, CitizenReportType
from app.schemas.citizen_report import (
    CitizenReportCreate,
    CitizenReportRead,
    CitizenReportDetail,
    CitizenReportVerifyPayload,
    NearbySensorMatchItem
)
from app.services.citizen_verification_engine import citizen_verification_engine
from app.core.deps import get_current_user, require_roles
from app.websocket.manager import ws_manager

router = APIRouter(prefix="/reports", tags=["Citizen Reports & Crowd-Sourcing"])


@router.post("", response_model=CitizenReportRead, status_code=status.HTTP_201_CREATED)
async def submit_citizen_report(
    payload: CitizenReportCreate,
    db: Session = Depends(get_db)
):
    """
    Submit a new geo-tagged citizen field report.
    Automatically evaluates proximity to physical sensors to compute an initial confidence score.
    """
    # Evaluate sensor correlation
    corroboration = citizen_verification_engine.correlate_report_with_sensors(
        db=db,
        latitude=payload.latitude,
        longitude=payload.longitude,
        report_type=payload.report_type,
        has_image=bool(payload.image_url)
    )

    new_report = CitizenReport(
        user_id=payload.user_id,
        report_type=payload.report_type,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        image_url=payload.image_url,
        verification_status=VerificationStatus.PENDING,
        confidence_score=corroboration["confidence_score"],
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    # Broadcast new report via WebSocket
    await ws_manager.broadcast_json({
        "type": "REPORT_CREATED",
        "data": {
            "id": new_report.id,
            "report_type": new_report.report_type.value if hasattr(new_report.report_type, "value") else str(new_report.report_type),
            "description": new_report.description,
            "latitude": new_report.latitude,
            "longitude": new_report.longitude,
            "confidence_score": new_report.confidence_score,
            "verification_status": "PENDING",
            "created_at": new_report.created_at.isoformat()
        }
    })

    return new_report


@router.get("", response_model=List[CitizenReportRead])
def get_citizen_reports(
    verification_status: Optional[str] = None,
    report_type: Optional[str] = None,
    verified_only: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get citizen reports with optional status and category filters.
    """
    query = db.query(CitizenReport)

    if verified_only:
        query = query.filter(CitizenReport.verification_status == VerificationStatus.VERIFIED)
    elif verification_status:
        query = query.filter(CitizenReport.verification_status == verification_status)

    if report_type:
        query = query.filter(CitizenReport.report_type == report_type)

    reports = query.order_by(desc(CitizenReport.created_at)).offset(offset).limit(limit).all()
    return reports


@router.get("/{report_id}", response_model=CitizenReportDetail)
def get_citizen_report_by_id(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed citizen report with nearby sensor telemetry correlation.
    """
    report = db.query(CitizenReport).filter(CitizenReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Citizen report not found.")

    # Re-evaluate live sensor matches
    corroboration = citizen_verification_engine.correlate_report_with_sensors(
        db=db,
        latitude=report.latitude,
        longitude=report.longitude,
        report_type=report.report_type,
        has_image=bool(report.image_url)
    )

    detail_data = CitizenReportDetail.model_validate(report)
    detail_data.confidence_score = corroboration["confidence_score"]
    detail_data.nearby_sensors_count = corroboration["nearby_sensors_count"]
    detail_data.corroborating_sensors_count = corroboration["corroborating_sensors_count"]
    detail_data.nearby_sensors = [NearbySensorMatchItem(**s) for s in corroboration["nearby_sensors"]]
    detail_data.matching_reasons = corroboration["matching_reasons"]

    return detail_data


@router.post("/{report_id}/verify", response_model=CitizenReportRead)
async def verify_citizen_report(
    report_id: int,
    payload: CitizenReportVerifyPayload,
    current_user: User = Depends(require_roles([
        UserRole.RESPONSE_TEAM,
        UserRole.GOVERNMENT_OFFICIAL,
        UserRole.ADMIN
    ])),
    db: Session = Depends(get_db)
):
    """
    Verify or reject a citizen ground truth report.
    Restricted to Response Team, Government Official, and Admin roles.
    """
    report = db.query(CitizenReport).filter(CitizenReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Citizen report not found.")

    report.verification_status = payload.verification_status
    report.verification_notes = payload.verification_notes
    report.verified_by_user_id = current_user.id
    report.verified_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(report)

    # Broadcast verification update via WebSocket
    await ws_manager.broadcast_json({
        "type": "REPORT_VERIFIED",
        "data": {
            "id": report.id,
            "status": report.verification_status.value if hasattr(report.verification_status, "value") else str(report.verification_status),
            "verified_by": current_user.name,
            "verified_at": report.verified_at.isoformat()
        }
    })

    return report
