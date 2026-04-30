"""
Turtle-ID Image Analysis Agents

Biolytics Agent: Strategy Pattern kullanarak deniz kaplumbağalarını türlerine göre tanımlama
- Green Turtle Strategy: Post-ocular scutes analizi
- Leatherback Strategy: Pineal spot analizi
"""

from .biolytics import (
    BiolyticsAgent,
    TurtleIdentificationStrategy,
    GreenTurtleStrategy,
    LeatherbackStrategy
)

__all__ = [
    'BiolyticsAgent',
    'TurtleIdentificationStrategy',
    'GreenTurtleStrategy',
    'LeatherbackStrategy'
]
