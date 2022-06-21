from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from bvrnapi.db.base_class import Base

# if TYPE_CHECKING:
#     from .association_homepage import AssociationHomepage  # noqa: F401


class Problem(Base):
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    data = Column(JSON)
    mtime = Column(DateTime)
    association_id = Column(Integer, ForeignKey("association.id"))

    association = relationship("Association", back_populates="problems")
