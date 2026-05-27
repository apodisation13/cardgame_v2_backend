class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserIncorrectPasswordError(Exception):
    pass


class ManageResourcesProcessError(Exception):
    pass


class NegativeResourcesError(Exception):
    pass


class UpgradeMaxLevelReachedError(Exception):
    pass


class CraftMillCardProcessError(Exception):
    pass


class PostStatsError(Exception):
    pass


class ProductDoesNotExistError(Exception):
    pass


class PurchaseDoesNotExistError(Exception):
    pass


class PaymentNotificationProcessError(Exception):
    pass
