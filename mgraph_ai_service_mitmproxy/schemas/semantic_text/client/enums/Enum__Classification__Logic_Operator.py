from enum import Enum


class Enum__Classification__Logic_Operator(str, Enum):                         # Logic operators for combining multiple criteria filters
    AND = 'and'                                                                # All criteria must match (intersection)
    OR  = 'or'                                                                 # Any criterion must match (union)
