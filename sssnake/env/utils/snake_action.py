from enum import unique, IntEnum


@unique
class SnakeAction(IntEnum):
    NONE = 0
    LEFT = 1
    RIGHT = 2

    @property
    def as_str(self) -> str:
        return {self.NONE: "none", self.LEFT: "left", self.RIGHT: "right"}[self]
