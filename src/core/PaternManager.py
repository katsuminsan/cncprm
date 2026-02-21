from enum import IntEnum
from pathlib import Path
import json

# 1. Enum definitions
class AxisType(IntEnum):
    L = 100
    S = 101
    A = 102
    T = 103
    NONE = 104

class ValueType(IntEnum):
    P = 10
    M = 11
    I = 12

class Format(IntEnum):
    Integer = 1
    Bit_8 = 2
    Decimal = 3

# 2. Load JSON file
json_path = Path("parameter_patterns.json")
with json_path.open("r", encoding="utf-8") as f:
    data = json.load(f)

# 3. Build lookup dictionaries
axis_lookup = {}
value_lookup = {}
format_lookup = {}

axis_mapping = {
    "AXIS_TYPE_NONE": AxisType.NONE,
    "AXIS_TYPE_L": AxisType.L,
    "AXIS_TYPE_S": AxisType.S,
    "AXIS_TYPE_A": AxisType.A,
    "AXIS_TYPE_T": AxisType.T
}

value_mapping = {
    "VALUE_TYPE_P": ValueType.P,
    "VALUE_TYPE_M": ValueType.M,
    "VALUE_TYPE_I": ValueType.I
}

format_mapping = {
    "Integer": Format.Integer,
    "Bit_8": Format.Bit_8,
    "Decimal": Format.Decimal
}

for key, item in data.items():
    N_number = item.get("N_number")
    if N_number:
        axis_lookup[N_number] = axis_mapping.get(item.get("axis_type"))
        value_lookup[N_number] = value_mapping.get(item.get("value_type"))
        format_lookup[N_number] = format_mapping.get(item.get("format"))

def getItem_By_N_number(n_index: int):
    pass

# 4. Functions to retrieve Enums or None
def get_axis_type(n_number: str):
    return axis_lookup.get(n_number)

def get_value_type(n_number: str):
    return value_lookup.get(n_number)

def get_format(n_number: str):
    return format_lookup.get(n_number)

if __name__ == '__main__':
    # Test with a few examples
    examples = ["N00000", "N00002", "N00981", "N01410"]
    for ex in examples:
        print(f"{ex}: AxisType={get_axis_type(ex)}, ValueType={get_value_type(ex)}, Format={get_format(ex)}")
    