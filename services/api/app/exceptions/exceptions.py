class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserIncorrectPasswordError(Exception):
    pass


class ManageResourcesProcessError(Exception):
    pass


class CraftMillCardProcessError(Exception):
    pass


class PostStatsError(Exception):
    pass


class ProductDoesNotExistError(Exception):
    pass


class PurchaseDoesNotExistError(Exception):
    pass
