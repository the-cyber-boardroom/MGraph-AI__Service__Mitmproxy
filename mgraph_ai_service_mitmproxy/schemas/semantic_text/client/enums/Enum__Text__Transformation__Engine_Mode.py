from enum import Enum

class Enum__Text__Transformation__Engine_Mode(str, Enum):                      # Engine modes for text transformation (determines selection logic)
    RANDOM         = 'random'                                                  # Pure random selection
    TEXT_HASH      = 'text_hash'                                               # Hash-based deterministic selection
    AWS_COMPREHEND = 'aws_comprehend'                                          # AWS Comprehend ML-based sentiment selection
    LLM            = 'llm'                                                     # LLM-based selection (future)
