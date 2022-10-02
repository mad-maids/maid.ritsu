import enum


class CarStatus(enum.Enum):

    DISABLE = 0
    ENABLE = 1


class OwnerStatus(enum.Enum):

    BANNED = 0
    ACTIVE = 1
