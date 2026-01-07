"""
Utils package initialization
Exports commonly used functions for easy importing
"""

from .loaders import load_inequality_data, load_geojson, load_all_indicators
from .utils import human_indicator, format_value, get_color_scale


from .insights import (
    generate_ranked_insights,      # NEW name
    format_insights_as_text,       # NEW name
    INSIGHT_TYPES
)


generate_insights = generate_ranked_insights
format_insights_text = format_insights_as_text

__all__ = [
    'load_inequality_data',
    'load_geojson',
    'load_all_indicators',
    'human_indicator',
    'format_value',
    'get_color_scale',
    'generate_ranked_insights',
    'generate_insights',           # Alias for backwards compatibility
    'format_insights_as_text',
    'format_insights_text',        # Alias for backwards compatibility
    'INSIGHT_TYPES'
]