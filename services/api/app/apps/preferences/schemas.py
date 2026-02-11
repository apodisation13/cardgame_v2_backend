from lib.utils.schemas import Base


DEFAULT_PREFERENCES = {
    "sound_on": True,
    "animation_on": True,
    "move_timeout": 1000,
    "avatar": None,
    "theme": 1,
}


class UserPreferencesResponse(Base):
    data: dict


class UpdateUserPreferencesRequest(Base):
    data: dict
