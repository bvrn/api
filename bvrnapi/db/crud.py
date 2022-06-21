from typing import List

from sqlalchemy.orm import Session

from bvrnapi.schemas.associations import Association
from bvrnapi.schemas.associations import AssociationCreate as AssociationModel

from .models import Association as AssociationDB
from .models import AssociationHomepage as AssociationHomepageDB


def get_homepage(db: Session, number: str):
    return (
        db.query(AssociationHomepageDB)
        .filter(AssociationHomepageDB.association_number == number)
        .first()
    )

def get_associations(db: Session, skip: int = 0, limit: int = 100):
    associations_db = db.query(AssociationDB).offset(skip).limit(limit).all()
    associations: List[Association] = []
    for accociation_db in associations_db:
        homepage = get_homepage(db, accociation_db.number)
        association_dict = {
            "shortname": accociation_db.shortname,
            "association_name": accociation_db.association_name,
            "city": accociation_db.city,
            "homepage": {
                "homepage": homepage.homepage,
                "impressum": homepage.impressum,
            },
            "representative": {
                "address": accociation_db.representative_address,
                "plz": accociation_db.representative_plz,
                "city": accociation_db.representative_city,
                "email": accociation_db.representative_email,
            },
            "it_representative": accociation_db.it_representative,
            "mtime": accociation_db.mtime,
        }
        associations.append(Association(**association_dict))
    return associations


def create_association(db: Session, association: AssociationModel):
    association_dict = association.dict()
    representative_dict = {
        f"representative_{k}": v
        for k, v in association_dict.pop("representative").items()
    }
    homepage_dict = association_dict.pop("homepage")

    association_db = AssociationDB(**association_dict, **representative_dict)
    db.add(association_db)
    db.commit()
    db.refresh(association_db)
    association_homepage_db = AssociationHomepageDB(**homepage_dict)
    db.add(association_homepage_db)
    db.commit()
    db.refresh(association_homepage_db)
    return association_db


def update_association(db: Session, number: str, association: AssociationModel):
    association_dict = association.dict()
    association_dict.update(
        {
            f"representative_{k}": v
            for k, v in association_dict.pop("representative").items()
        }
    )
    homepage_dict = association_dict.pop("homepage")

    association_db = get_association(db, number)
    association_db.update(association_dict, synchronize_session=False)
    db.commit()
    db.refresh(association_db)
    association_homepage_db = get_homepage(db, number)
    association_homepage_db.update(homepage_dict, synchronize_session=False)
    db.commit()
    db.refresh(association_homepage_db)

    return association_db
