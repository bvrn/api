# Import all the models, so that Base has them before being
# imported by Alembic
from bvrnapi.db.base_class import Base # noqa
from bvrnapi.models.association import Association # noqa
