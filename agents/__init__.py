"""
Agents module - bevat agent definities, CV data en kennisbank.
"""

from .definitions import Agent, AGENTEN
from .cv_data import CV_DATA
from .kennisbank import (
    KENNIS_PRO, 
    KENNIS_CONTRA, 
    MAX_VERSTAPPEN_FEITEN, 
    YOGA_FEITEN
)

__all__ = [
    'Agent',
    'AGENTEN', 
    'CV_DATA',
    'KENNIS_PRO',
    'KENNIS_CONTRA',
    'MAX_VERSTAPPEN_FEITEN',
    'YOGA_FEITEN',
]
