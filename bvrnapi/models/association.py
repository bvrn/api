from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from bvrnapi.db.base_class import Base


class Association(Base):
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True, unique=True)
    shortname = Column(String)
    association_name = Column(String, index=True, unique=True)
    city = Column(String)
    representative_address = Column(String)
    representative_plz = Column(Integer)
    representative_city = Column(String)
    representative_email = Column(String)
    it_representative = Column(String)
    mtime = Column(DateTime)
    homepage = Column(String, index=True)
    impressum = Column(String)

    problems = relationship("Problem", back_populates="association")
