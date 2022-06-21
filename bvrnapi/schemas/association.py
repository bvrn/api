from typing import Optional, Union

from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, HttpUrl

from bvrnapi.schemas.additional import Representative

# TODO: edit
from bvrnapi.schemas.httpurl_status import HttpsUrlStatus, HttpUrlStatus

# ar_example = {
#     "shortname": "MV Musik",
#     "association_name": "Musikverein Musik e.V.",
#     "city": "Heidelberg",
#     "representative": {
#         "address": "Blasmusikweg 1",
#         "plz": 69120,
#         "city": "Heidelberg",
#         "email": "Vorstand Musik <vorstand@example.com>",
#     },
#     "it_representative": "Administrierende <admin@example.com>",
#     "mtime": datetime.today(),
# }


# Shared properties
class AssociationBase(BaseModel):
    number: constr(regex=r"^11152A\d{3}$")
    shortname: Optional[str]
    association_name: str
    city: str
    representative: Representative
    it_representative: EmailStr
    mtime: datetime
    homepage: Union[HttpsUrlStatus, HttpUrlStatus, None]
    impressum: Optional[HttpUrl]

    # class Config:
    #     schema_extra = {"example": ar_example}


# Properties to receive via API on creation
class AssociationCreate(AssociationBase):
    pass


# Properties to receive via API on update
class AssociationUpdate(AssociationBase):
    pass


# Properties shared by models stored in DB
class AssociationInDBBase(AssociationBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Association(AssociationInDBBase):
    pass


# Additional properties stored in DB
class AssociationInDB(AssociationInDBBase):
    pass
