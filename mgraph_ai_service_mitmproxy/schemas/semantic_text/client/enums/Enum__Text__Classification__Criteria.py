from enum import Enum


class Enum__Text__Classification__Criteria(str, Enum):                         # Classification criteria matching AWS Comprehend sentiment scores
    POSITIVE = 'positive'                                                       # Positive sentiment score (0.0-1.0)
    NEGATIVE = 'negative'                                                       # Negative sentiment score (0.0-1.0)
    NEUTRAL  = 'neutral'                                                        # Neutral sentiment score (0.0-1.0)
    MIXED    = 'mixed'                                                          # Mixed sentiment score (0.0-1.0)
