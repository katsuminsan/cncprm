from dataclasses import dataclass
from enum import Enum
from decimal import Decimal


class ValueType(Enum):
    P = "P"
    M = "M"
    I = "I"

class ValueFormat(Enum):
    BIT_8 = "Bit_8"
    DECIMAL = "Decimal"
    INT = "Integer"


class IntegerOperations:
    def get(self, v, type="int"):
        '''
        get value function.
        
        - type: set str in ["str", "int", "float"]
        '''

        if type == "int":
            return int(v)
        if type == "str":
            return str(v)
        if type == "float":
            return float(v)
        
    def set(self, v):
        '''
        set value function.
        '''
        if not isinstance(v, (int, str)):
            raise ValueError("set_value must be integer or str.")
        
        new_v = str(v)

        return new_v


class DecimalOperations:
    def get(self, v, type="Decimal"):
        '''
        get value function.
        
        - type: set str in ["Decimal", "str", "int", "float"]
        '''

        if type == "Decimal":
            return Decimal(v)
        
        if type == "str":
            return str(v)
        
        if type == "float":
            return float(v)
        
        if type == "int":
            return int(v)
       
    def set(self, v):
        try:
            if v.isdigit():
                new_v = str(v)
        except ValueError:
            raise ValueError("set_value must be integer, float or str.and only digits")
        return new_v
        
class BitOperations:
    def get_bit(self, v, index):
        if isinstance(v, str):
            if not len(v) == 8:
                raise ValueError("if v is type str,its length must be 8")
            str_v = v
        elif isinstance(v, int):
            if not v <= int("11111111", 2):
                raise ValueError("if v is type int, the value of v must be less than or equal to 255 in binary")
            str_v = f'{v:08b}'

        if not (0 <= index < 8):
            raise IndexError("Bit index out of range (must be 0-7)")
        return str_v[index]

    def set_bit(self, v, index, bit):
        if not hasattr(self, "value"):
            raise AttributeError("The class does not have a 'value' attribute")
        if not (0 <= index < 8):
            raise IndexError("Bit index out of range (must be 0-7)")
        if bit not in {"0", "1"}:
            raise ValueError("Bit must be '0' or '1'")
        new_value = list(v)
        new_value[index] = bit
        object.__setattr__(self, "value", "".join(new_value))


@dataclass(frozen=True)
class TypedValue():
    value_type: ValueType
    value_format: ValueFormat
    value: str
    raw: None
    
    @staticmethod
    def parse_raw(raw):
        if raw[:1] == "P":
            v_type = ValueType.P
        if raw[:1] == "M":
            v_type = ValueType.M
        if raw[:1] == "I":
            v_type = ValueType.I
        v_value = raw[1:]
        if len(v_value) == 8 and set(v_value).issubset({0, 1}):
            return TypedValue(v_type, ValueFormat.BIT_8, v_value, raw)

        if "." in v_value:
            try:
                return TypedValue(v_type, ValueFormat.BIT_8, v_value, raw)
            except ValueError:
                return None
        
        if v_value.isdigit():
            return TypedValue(v_type, ValueFormat.INT, v_value, raw)
        
    def serialize(self):
        if self.raw is not None:
            return self.raw
        return f'{self.value_type}{self.value}'
    
    def set_value(self, set_v):
        if self.value_format != ValueFormat.BIT_8:
            pass


