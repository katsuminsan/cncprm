from dataclasses import dataclass
from enum import Enum


class AxisType(Enum):
    NONE = "AXIS_TYPE_NONE"
    A = "AXIS_TYPE_A"
    S = "AXIS_TYPE_S"
    T = "AXIS_TYPE_T"
    L = "AXIS_TYPE_L"

class ValueType(Enum):
    P = "VALUE_TYPE_P"
    M = "VALUE_TYPE_M"
    I = "VALUE_TYPE_I"

class FormatType(Enum):
    BIT_8 = "Bit_8"
    DECIMAL = "Decimal"
    INTEGER = "Integer"


@dataclass(frozen=True)
class IndexType():
    raw: str
    kind: AxisType


@dataclass(frozen=True)
class TypeValue():
    raw: int
    kind: ValueType
    format: FormatType


@dataclass(frozen=True)
class Parameter():
    number: int
    body: tuple[TypeValue, ...]


class ParameterSet():
    __slots__ = ('_map, ')

    def __init__(self):
        pass