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
