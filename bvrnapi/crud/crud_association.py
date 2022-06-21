from typing import List, Optional, Dict, Any, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from bvrnapi.crud.base import CRUDBase
from bvrnapi.models.association import Association
from bvrnapi.schemas.association import AssociationCreate, AssociationUpdate


class CRUDAssociation(CRUDBase[Association, AssociationCreate, AssociationUpdate]):
    def get_by_number(self, db: Session, *, number: str) -> Optional[Association]:
        return db.query(Association).filter(Association.number == number).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[Association]:
        return db.query(Association).filter(Association.association_name == name).first()

    def get_by_city(self, db: Session, *, city: str) -> List[Association]:
        return db.query(self.model).filter(Association.city == city).all()

    def create(self, db: Session, *, obj_in: AssociationCreate) -> Association:
        obj_in_data = jsonable_encoder(obj_in)
        representative_dict = {
            f"representative_{k}": v
            for k, v in obj_in_data.pop("representative").items()
        }
        db_obj = self.model(**obj_in_data, **representative_dict)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: Association,
        obj_in: Union[AssociationUpdate, Dict[str, Any]]
    ) -> Association:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "representative" in update_data:
            representative_obj = update_data.pop("representative")
            if isinstance(representative_obj, dict):
                representative_dict = representative_obj
            else:
                representative_dict = representative_obj.dict(exclude_unset=True)
            update_data.update({
                f"representative_{k}": v
                for k, v in representative_dict.items()
            })
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


association = CRUDAssociation(Association)
