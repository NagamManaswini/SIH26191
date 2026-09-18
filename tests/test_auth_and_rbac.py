import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.models.enums import UserRole

client = TestClient(app)

@pytest.fixture
def unique_citizen_data():
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "name": f"Citizen Test {timestamp}",
        "email": f"citizen_{timestamp}@test.org",
        "password": "SecurePassword123!",
        "role": "CITIZEN",
        "district": "Rudraprayag",
        "state": "Uttarakhand",
        "phone": "+91-9876543210"
    }

@pytest.fixture
def unique_researcher_data():
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "name": f"Researcher Test {timestamp}",
        "email": f"researcher_{timestamp}@test.org",
        "password": "SecurePassword123!",
        "role": "RESEARCHER",
        "district": "Nainital",
        "state": "Uttarakhand"
    }

@pytest.fixture
def unique_response_team_data():
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "name": f"Responder Test {timestamp}",
        "email": f"responder_{timestamp}@test.org",
        "password": "SecurePassword123!",
        "role": "RESPONSE_TEAM",
        "district": "Chamoli",
        "state": "Uttarakhand"
    }

@pytest.fixture
def unique_gov_data():
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "name": f"Gov Test {timestamp}",
        "email": f"gov_{timestamp}@test.org",
        "password": "SecurePassword123!",
        "role": "GOVERNMENT_OFFICIAL",
        "district": "Dehradun",
        "state": "Uttarakhand"
    }

@pytest.fixture
def unique_admin_data():
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    return {
        "name": f"Admin Test {timestamp}",
        "email": f"admin_{timestamp}@test.org",
        "password": "SecurePassword123!",
        "role": "ADMIN",
        "district": "Central",
        "state": "Uttarakhand"
    }

def test_user_registration_success(unique_citizen_data):
    """Test successful user registration and JWT token generation."""
    response = client.post("/api/auth/register", json=unique_citizen_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == unique_citizen_data["email"]
    assert data["user"]["role"] == "CITIZEN"

def test_duplicate_registration_fails(unique_citizen_data):
    """Test duplicate registration with existing email returns 400."""
    response1 = client.post("/api/auth/register", json=unique_citizen_data)
    assert response1.status_code == 201

    response2 = client.post("/api/auth/register", json=unique_citizen_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

def test_login_valid_credentials(unique_citizen_data):
    """Test valid user login."""
    client.post("/api/auth/register", json=unique_citizen_data)

    login_payload = {
        "email": unique_citizen_data["email"],
        "password": unique_citizen_data["password"]
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == unique_citizen_data["email"]

def test_login_invalid_password(unique_citizen_data):
    """Test invalid password login returns 401."""
    client.post("/api/auth/register", json=unique_citizen_data)

    login_payload = {
        "email": unique_citizen_data["email"],
        "password": "WrongPassword999!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_login_nonexistent_user():
    """Test login for unregistered user returns 401."""
    login_payload = {
        "email": "nonexistent_ghost_user@flashflood.org",
        "password": "AnyPassword123!"
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_get_current_user_profile(unique_citizen_data):
    """Test GET /api/auth/me returns the logged in user profile."""
    reg = client.post("/api/auth/register", json=unique_citizen_data)
    token = reg.json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    user_info = response.json()
    assert user_info["email"] == unique_citizen_data["email"]
    assert user_info["role"] == "CITIZEN"

def test_protected_endpoint_without_jwt():
    """Test accessing protected route without JWT returns 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "missing" in response.json()["detail"].lower()

def test_protected_endpoint_with_invalid_jwt():
    """Test accessing protected route with forged or expired JWT returns 401."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_gibberish_token_value_xyz"}
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_role_based_access_control(
    unique_citizen_data,
    unique_researcher_data,
    unique_response_team_data,
    unique_gov_data,
    unique_admin_data
):
    """
    Test RBAC authorization:
    - Citizen can access citizen portal, but not research, response, gov, or admin.
    - Researcher can access research analytics.
    - Response Team can access response status.
    - Gov Official can access response status (inherited) and gov command.
    - Admin can access all endpoints including admin user management.
    """
    # 1. Register users for all roles
    citizen_token = client.post("/api/auth/register", json=unique_citizen_data).json()["access_token"]
    researcher_token = client.post("/api/auth/register", json=unique_researcher_data).json()["access_token"]
    response_token = client.post("/api/auth/register", json=unique_response_team_data).json()["access_token"]
    gov_token = client.post("/api/auth/register", json=unique_gov_data).json()["access_token"]
    admin_token = client.post("/api/auth/register", json=unique_admin_data).json()["access_token"]

    # --- Citizen Access Tests ---
    # Citizen -> Citizen Portal: 200
    res = client.get("/api/rbac/citizen/portal", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res.status_code == 200
    assert res.json()["access"] == "granted"

    # Citizen -> Research Analytics: 403 (Wrong role)
    res = client.get("/api/rbac/research/analytics", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res.status_code == 403

    # Citizen -> Response Command: 403
    res = client.get("/api/rbac/response/status", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res.status_code == 403

    # Citizen -> Admin Users: 403
    res = client.get("/api/rbac/admin/users", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res.status_code == 403

    # --- Researcher Access Tests ---
    # Researcher -> Research Analytics: 200
    res = client.get("/api/rbac/research/analytics", headers={"Authorization": f"Bearer {researcher_token}"})
    assert res.status_code == 200
    assert "view_predictions" in res.json()["capabilities"]

    # Researcher -> Admin Users: 403
    res = client.get("/api/rbac/admin/users", headers={"Authorization": f"Bearer {researcher_token}"})
    assert res.status_code == 403

    # --- Response Team Access Tests ---
    # Response Team -> Response Status: 200
    res = client.get("/api/rbac/response/status", headers={"Authorization": f"Bearer {response_token}"})
    assert res.status_code == 200

    # Response Team -> Gov Command: 403
    res = client.get("/api/rbac/gov/command", headers={"Authorization": f"Bearer {response_token}"})
    assert res.status_code == 403

    # --- Government Official Access Tests (Inheritance) ---
    # Gov Official -> Response Status (Inherited): 200
    res = client.get("/api/rbac/response/status", headers={"Authorization": f"Bearer {gov_token}"})
    assert res.status_code == 200

    # Gov Official -> Gov Command: 200
    res = client.get("/api/rbac/gov/command", headers={"Authorization": f"Bearer {gov_token}"})
    assert res.status_code == 200

    # Gov Official -> Admin Users: 403
    res = client.get("/api/rbac/admin/users", headers={"Authorization": f"Bearer {gov_token}"})
    assert res.status_code == 403

    # --- Admin Access Tests (Superuser / All Features) ---
    # Admin -> Citizen Portal: 200
    assert client.get("/api/rbac/citizen/portal", headers={"Authorization": f"Bearer {admin_token}"}).status_code == 200
    # Admin -> Research Analytics: 200
    assert client.get("/api/rbac/research/analytics", headers={"Authorization": f"Bearer {admin_token}"}).status_code == 200
    # Admin -> Response Status: 200
    assert client.get("/api/rbac/response/status", headers={"Authorization": f"Bearer {admin_token}"}).status_code == 200
    # Admin -> Gov Command: 200
    assert client.get("/api/rbac/gov/command", headers={"Authorization": f"Bearer {admin_token}"}).status_code == 200
    # Admin -> Admin Users: 200
    res = client.get("/api/rbac/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert len(res.json()) >= 1

def test_permissions_matrix_public():
    """Test public permissions matrix endpoint."""
    res = client.get("/api/rbac/permissions-matrix")
    assert res.status_code == 200
    data = res.json()
    assert "CITIZEN" in data
    assert "RESEARCHER" in data
    assert "RESPONSE_TEAM" in data
    assert "GOVERNMENT_OFFICIAL" in data
    assert "ADMIN" in data
