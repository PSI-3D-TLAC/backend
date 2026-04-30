import StavPlatby


class Platba:
    id: int
    amount: float
    status: StavPlatby.StavPlatby
    paymentMethod: str

    def __init__(self, id: int, amount: float, status: StavPlatby.StavPlatby, paymentMethod: str):
        self.id = id
        self.amount = amount
        self.status = status
        self.paymentMethod = paymentMethod
