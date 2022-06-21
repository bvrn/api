from pydantic import BaseModel, EmailStr


class Representative(BaseModel):
    address: str
    plz: int
    city: str
    email: EmailStr