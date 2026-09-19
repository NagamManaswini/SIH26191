"""Test database connection, schema creation, and session lifecycle."""

from sqlalchemy import text, inspect


def test_database_connection(db):
    """Test executing basic query on database connection."""
    result = db.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_tables_created(db):
    """Test that all 12 model tables exist in metadata."""
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    expected_tables = [
        "users",
        "locations",
        "population",
        "shelters",
        "shelter_resources",
        "roads",
        "hazard_zones",
        "rainfall_records",
        "disaster_events",
        "evacuation_routes",
        "relocation_assignments",
        "alerts",
    ]
    for table in expected_tables:
        assert table in tables, f"Table '{table}' missing from database"
