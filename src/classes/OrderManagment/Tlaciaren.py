import StavTlaciarne

class Tlaciaren:
    id: int
    precision: float
    status: StavTlaciarne.StavTlaciarne

    def __init__(self, id: int, precision: float, status: StavTlaciarne.StavTlaciarne):
        self.id = id
        self.precision = precision
        self.status = status

    def reserve(self) -> bool:
        if self.status != StavTlaciarne.StavTlaciarne.AVAILABLE:
            return False
        self.status = StavTlaciarne.StavTlaciarne.RESERVED
        return True

    def startPrint(self, item) -> bool:
        if self.status not in (StavTlaciarne.StavTlaciarne.AVAILABLE, StavTlaciarne.StavTlaciarne.RESERVED):
            return False
        self.status = StavTlaciarne.StavTlaciarne.PRINTING
        return True

    def finishPrint(self):
        self.status = StavTlaciarne.StavTlaciarne.AVAILABLE

    def setOutOfService(self):
        self.status = StavTlaciarne.StavTlaciarne.OUT_OF_SERVICE

    def isAvailable(self) -> bool:
        return self.status == StavTlaciarne.StavTlaciarne.AVAILABLE
