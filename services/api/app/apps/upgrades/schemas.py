from lib.utils.schemas import Base
from lib.utils.schemas.game import UpgradeSubtype, UpgradeType
from services.api.app.apps.progress.schemas import UserResources


class PostUpgradeRequest(Base):
    upgrade_type: UpgradeType
    upgrade_subtype: UpgradeSubtype


class PostUpgradeResponse(Base):
    upgrades: dict
    resources: UserResources
