"""
Utils package initialization
Exports commonly used functions for easy importing
"""

from .loaders import load_inequality_data
from .utils import human_indicator


from .insights import (
    generate_ranked_insights,      # NEW name
    format_insights_as_text,       # NEW name
    INSIGHT_TYPES
)


generate_insights = generate_ranked_insights
format_insights_text = format_insights_as_text

__all__ = [
    'load_inequality_data',
    'human_indicator',
    'generate_ranked_insights',
    'generate_insights',           # Alias for backwards compatibility
    'format_insights_as_text',
    'format_insights_text',        # Alias for backwards compatibility
    'INSIGHT_TYPES'
]