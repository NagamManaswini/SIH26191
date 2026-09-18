from app.crud.base import CRUDBase
from app.crud.crud_sensor import sensor_crud
from app.crud.crud_readings import rainfall_crud, river_crud, soil_moisture_crud
from app.crud.crud_watershed import watershed_crud

__all__ = [
    "CRUDBase",
    "sensor_crud",
    "rainfall_crud",
    "river_crud",
    "soil_moisture_crud",
    "watershed_crud",
]
