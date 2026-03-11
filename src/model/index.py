from dataclasses import dataclass
from enum import Enum

class IndexType(Enum):
    AXIS = "A"
    SPINDLE = "S"
    LINE = "L"
    TYPE = "T"
    NONE = ""


@dataclass(frozen=True)
class Index:
    '''
    Repesents an index such as A1, S2 etc...
    '''
    type = None
    number = None

    def __hash__(self):
        return hash((self.type, self.number))
