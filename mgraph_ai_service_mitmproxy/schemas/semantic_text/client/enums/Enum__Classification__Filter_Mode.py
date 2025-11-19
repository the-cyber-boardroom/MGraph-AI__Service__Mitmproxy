from enum import Enum


class Enum__Classification__Filter_Mode(str, Enum):                            # Filter comparison operations for classification criteria
    ABOVE   = 'above'                                                          # rating > threshold
    BELOW   = 'below'                                                          # rating < threshold