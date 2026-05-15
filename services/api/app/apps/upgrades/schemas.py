from lib.utils.schemas import Base
from lib.utils.schemas.game import UpgradeType, UpgradeSubtype


class PostUpgradeRequest(Base):
    upgrade_type: UpgradeType
    upgrade_subtype: UpgradeSubtype
