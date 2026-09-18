from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.core.deps import get_current_user, require_roles
from app.schemas.user import UserRead

router = APIRouter(prefix="/rbac", tags=["Role-Based Access Control"])

@router.get("/citizen/portal")
def citizen_portal(
    current_user: User = Depends(require_roles([UserRole.CITIZEN]))
) -> Dict[str, Any]:
    """
    Accessible by CITIZEN (and ADMIN).
    """
    return {
        "access": "granted",
        "role": current_user.role,
        "message": "Welcome to Citizen Disaster Reporting Portal",
        "capabilities": ["view_public_flood_risk", "view_alerts", "submit_citizen_reports", "view_evacuation_centers"]
    }

@router.get("/research/analytics")
def research_analytics(
    current_user: User = Depends(require_roles([UserRole.RESEARCHER]))
) -> Dict[str, Any]:
    """
    Accessible by RESEARCHER (and ADMIN).
    """
    return {
        "access": "granted",
        "role": current_user.role,
        "message": "Welcome to Advanced Hydrological Research & Model Analytics",
        "capabilities": ["view_sensors", "view_historical_data", "view_predictions", "view_analytics"]
    }

@router.get("/response/status")
def response_team_status(
    current_user: User = Depends(require_roles([UserRole.RESPONSE_TEAM]))
) -> Dict[str, Any]:
    """
    Accessible by RESPONSE_TEAM, GOVERNMENT_OFFICIAL, and ADMIN.
    """
    return {
        "access": "granted",
        "role": current_user.role,
        "message": "Emergency Response & Evacuation Dispatch Command",
        "capabilities": ["view_live_sensors", "view_predictions", "view_alerts", "view_evacuation_routes", "update_response_status"]
    }

@router.get("/gov/command")
def government_command(
    current_user: User = Depends(require_roles([UserRole.GOVERNMENT_OFFICIAL]))
) -> Dict[str, Any]:
    """
    Accessible by GOVERNMENT_OFFICIAL (and ADMIN).
    """
    return {
        "access": "granted",
        "role": current_user.role,
        "message": "Government Disaster Management Executive Console",
        "capabilities": ["all_response_team_capabilities", "analytics", "manage_alerts", "manage_evacuation_centers"]
    }

@router.get("/admin/users", response_model=List[UserRead])
def admin_user_management(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
) -> Any:
    """
    Accessible ONLY by ADMIN.
    """
    users = db.query(User).all()
    return users

@router.get("/permissions-matrix")
def permissions_matrix() -> Dict[str, Any]:
    """
    Public metadata listing all supported roles and their exact permission sets.
    """
    return {
        "CITIZEN": {
            "title": "Citizen / Community Volunteer",
            "permissions": [
                "view_public_flood_risk",
                "view_alerts",
                "submit_citizen_reports",
                "view_evacuation_centers"
            ],
            "description": "Public hazard awareness, emergency notifications, and local ground report submissions."
        },
        "RESEARCHER": {
            "title": "Hydrological Researcher / Academic",
            "permissions": [
                "view_sensors",
                "view_historical_data",
                "view_predictions",
                "view_analytics"
            ],
            "description": "Deep telemetry analysis, catchment runoff studies, historical flood replay, and model benchmarking."
        },
        "RESPONSE_TEAM": {
            "title": "First Responder / NDRF / SDRF",
            "permissions": [
                "view_live_sensors",
                "view_predictions",
                "view_alerts",
                "view_evacuation_routes",
                "update_response_status"
            ],
            "description": "Real-time flood front tracking, safe rescue route navigation, and field incident status dispatch."
        },
        "GOVERNMENT_OFFICIAL": {
            "title": "District Magistrate / Disaster Authority Officer",
            "permissions": [
                "view_live_sensors",
                "view_predictions",
                "view_alerts",
                "view_evacuation_routes",
                "update_response_status",
                "analytics",
                "manage_alerts",
                "manage_evacuation_centers"
            ],
            "description": "Executive emergency command, alert broadcast management, and evacuation shelter capacity coordination."
        },
        "ADMIN": {
            "title": "System Administrator",
            "permissions": [
                "user_management",
                "sensor_management",
                "system_configuration",
                "all_features"
            ],
            "description": "Full root-level administration, sensor grid deployment, user credential management, and IoT integrations."
        }
    }
