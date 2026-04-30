import StavTlaciarne


class Tlaciaren:
    id: int
    precision: float
    status: StavTlaciarne.StavTlaciarne

    def __init__(self, id: int, precision: float, status: StavTlaciarne.StavTlaciarne):
        self.id = id
        self.precision = precision
        self.status = status
