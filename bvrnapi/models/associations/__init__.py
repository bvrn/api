from __future__ import annotations

from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, EmailStr, HttpUrl, constr

from bvrnapi.models.httpurl_status import HttpsUrlStatus, HttpUrlStatus

ar_example = {
    "shortname": "MV Musik",
    "association_name": "Musikverein Musik e.V.",
    "city": "Heidelberg",
    "homepage": {
        "homepage": "https://example.com",
        "impressum": "https://example.com/impressum",
    },
    "representative": {
        "address": "Blasmusikweg 1",
        "plz": 69120,
        "city": "Heidelberg",
        "email": "Vorstand Musik <vorstand@example.com>",
    },
    "it_representative": "Administrierende <admin@example.com>",
    "mtime": datetime.today(),
}


class Representative(BaseModel):
    address: str
    plz: int
    city: str
    email: EmailStr


class AssociationBase(BaseModel):
    shortname: Optional[str]
    association_name: str
    city: str
    representative: Representative
    it_representative: EmailStr
    mtime: datetime

    class Config:
        schema_extra = {"example": ar_example}


class AssociationCreate(AssociationBase):
    number: constr(regex=r"^11152A\d{3}$")
    homepage: AssociationHomepageCreate


class Association(AssociationBase):
    homepage: AssociationHomepage

    class Config:
        orm_mode = True


class AssociationHomepageBase(BaseModel):
    impressum: Optional[HttpUrl]


class AssociationHomepageCreate(AssociationHomepageBase):
    homepage: Union[HttpsUrlStatus, HttpUrlStatus, None]
    association_number: constr(regex=r"^11152A\d{3}$")


class AssociationHomepage(AssociationHomepageBase):
    homepage: Optional[HttpUrl]

    class Config:
        orm_mode = True


# https://github.com/samuelcolvin/pydantic/issues/1298#issuecomment-737642051
AssociationCreate.update_forward_refs()
Association.update_forward_refs()
