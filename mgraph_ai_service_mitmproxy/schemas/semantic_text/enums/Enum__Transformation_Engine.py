from enum import Enum

class Enum__Transformation_Engine(str, Enum):                                                  # Text transformation engines available
    AWS_COMPREHEND = "aws-comprehend"                                                          # AWS Comprehend PII detection
    TEXT_HASH      = "text-hash"                                                               # Deterministic hash-based
    RANDOM         = "random"                                                                  # Random character replacement

    # todo see why we need these
    # def to_config(self) -> dict:                                                               # Convert engine type to transformation_engine
    #     return { "engine"        : self.value,
    #              "engine_config" : {}      }

    # @classmethod
    # def from_string(cls, value: str) -> 'Enum__Transformation_Engine':                         # Parse from string value
    #     try:
    #         return cls(value.lower())
    #     except ValueError:
    #         return cls.TEXT_HASH                                                               # Default to deterministic