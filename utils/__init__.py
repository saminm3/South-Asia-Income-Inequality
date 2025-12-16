"""
Utils package for South Asia Inequality Analysis Platform
"""

from .loaders import load_inequality_data, load_geojson, load_quality_audit, load_all_indicators
from .utils import human_indicator, format_value, handle_missing_data
from .insights import generate_insights, format_insights_text

__all__ = [
    'load_inequality_data',
    'load_geojson',
    'load_quality_audit',
    'load_all_indicators',
    'human_indicator',
    'format_value',
    'handle_missing_data',
    'generate_insights',
    'format_insights_text'
]