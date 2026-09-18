from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.watershed import Watershed
from app.schemas.watershed import WatershedCreate, WatershedUpdate

class CRUDWatershed(CRUDBase[Watershed, WatershedCreate, WatershedUpdate]):
    def get_by_code(self, db: Session, code: str) -> Optional[Watershed]:
        stmt = select(Watershed).where(Watershed.code == code)
        return db.scalars(stmt).first()

watershed_crud = CRUDWatershed(Watershed)
