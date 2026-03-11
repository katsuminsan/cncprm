from dataclasses import dataclass

@dataclass(frozen=True)
class ValueArray:
    '''
    Mapping Index -> TypedVlaue
    '''
    values = None
    axis_map = None

    @staticmethod
    def create():
        return ValueArray({}, {[]})
    
