"""
Utils package initialization
Exports commonly used functions for easy importing
"""

from .loaders import load_inequality_data, load_geojson, load_all_indicators
from .utils import human_indicator, format_value, get_color_scale

__all__ = [
    'load_inequality_data',
    'load_geojson',
    'load_all_indicators',
    'human_indicator',
    'format_value',
    'get_color_scale'
]