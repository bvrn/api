from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Association(Base):
    __tablename__ = "association"

    number = Column(String, primary_key=True, index=True, unique=True)
    shortname = Column(String)
    association_name = Column(String)
    city = Column(String)
    representative_address = Column(String)
    representative_plz = Column(Integer)
    representative_city = Column(String)
    representative_email = Column(String)
    it_representative = Column(String)
    mtime = Column(DateTime)
    homepage = relationship(
        "AssociationHomepage", back_populates="association", uselist=False
    )  # one to one


class AssociationHomepage(Base):
    __tablename__ = "association_homepage"

    association_number = Column(
        String,
        ForeignKey("association.number"),
        primary_key=True,
        index=True,
        unique=True,
    )
    homepage = Column(String)
    impressum = Column(String)
    association = relationship("Association", back_populates="homepage")
