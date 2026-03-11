from dataclasses import dataclass


@dataclass(frozen=True)
class ParameterKey():
    '''
    Parameter identifier.
    
    - number: parameter number (Nxxxxxx)
    - sub_index: reserved for future extention
    - array_index: reserved for future extention
    '''
    number = None
    sub_index = None
    array_index = None
