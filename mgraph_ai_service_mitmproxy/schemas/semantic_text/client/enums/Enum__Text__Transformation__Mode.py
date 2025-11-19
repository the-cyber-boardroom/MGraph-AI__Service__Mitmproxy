from enum import Enum


class Enum__Text__Transformation__Mode(str, Enum):                              # Text transformation modes for semantic analysis
    XXX            = 'xxx'                                                      # Randomly mask text with 'x' characters
    HASHES         = 'hashes'                                                   # Randomly show text as hash values
    ABCDE_BY_SIZE  = 'abcde-by-size'                                            # Group text by length, replace with letters (a,b,c,d,e)