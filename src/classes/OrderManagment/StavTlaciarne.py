from enum import Enum

class StavTlaciarne(Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    PRINTING = "PRINTING"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"
