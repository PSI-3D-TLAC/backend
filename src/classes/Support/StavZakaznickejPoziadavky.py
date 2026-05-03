from enum import Enum

class StavZakaznickejPoziadavky(Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
