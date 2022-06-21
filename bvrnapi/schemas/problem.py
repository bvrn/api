from enum import Enum
from typing import Optional, Union

from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, HttpUrl


class ProblemType(str, Enum):
    city_not_found = "city_not_found"
    homepage = "homepage"
    impressum_no_http_url = "impressum_no_http_url"
    impressum_not_found = "impressum_not_found"


# Shared properties
class ProblemBase(BaseModel):
    type: ProblemType
    data: dict = dict()
    mtime: datetime = datetime.now()


# Properties to receive via API on creation
class ProblemCreate(ProblemBase):
    pass


# Properties to receive via API on update
class ProblemUpdate(ProblemBase):
    pass


# Properties shared by models stored in DB
class ProblemInDBBase(ProblemBase):

    id: Optional[int] = None
    association_id: int

    class Config:
        orm_mode = True


# Additional properties to return via API
class Problem(ProblemInDBBase):
    pass


# Additional properties stored in DB
class ProblemInDB(ProblemInDBBase):
    pass
