"""Base spatial type decorators supporting PostgreSQL/PostGIS and fallback to WKT String."""

from sqlalchemy import String, TypeDecorator, text
try:
    from geoalchemy2 import Geometry
except Exception:
    Geometry = None

_HAS_POSTGIS = None


def check_postgis(dialect):
    """Check if PostGIS extension is available in the connected PostgreSQL database."""
    global _HAS_POSTGIS
    if Geometry is None or dialect is None or getattr(dialect, "name", "") != "postgresql":
        return False
    if _HAS_POSTGIS is not None:
        return _HAS_POSTGIS

    try:
        # Check if the active connection has PostGIS extension loaded
        with dialect.connect() as conn:
            res = conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")).scalar()
            _HAS_POSTGIS = bool(res)
    except Exception:
        _HAS_POSTGIS = False

    return _HAS_POSTGIS


class SpatialPoint(TypeDecorator):
    """Point geometry type that uses PostGIS when available, otherwise String (WKT)."""

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if Geometry is not None and check_postgis(dialect):
            geom = Geometry(geometry_type="POINT", srid=4326)
            return dialect.type_descriptor(geom) if dialect is not None else geom
        return dialect.type_descriptor(String())


    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)


class SpatialPolygon(TypeDecorator):
    """Polygon geometry type that uses PostGIS when available, otherwise String (WKT)."""

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if Geometry is not None and check_postgis(dialect):
            geom = Geometry(geometry_type="POLYGON", srid=4326)
            return dialect.type_descriptor(geom) if dialect is not None else geom
        return dialect.type_descriptor(String())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)


class SpatialLineString(TypeDecorator):
    """LineString geometry type that uses PostGIS when available, otherwise String (WKT)."""

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if Geometry is not None and check_postgis(dialect):
            geom = Geometry(geometry_type="LINESTRING", srid=4326)
            return dialect.type_descriptor(geom) if dialect is not None else geom
        return dialect.type_descriptor(String())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)

