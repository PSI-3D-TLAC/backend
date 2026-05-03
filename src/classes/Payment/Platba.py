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

    def process(self) -> bool:
        self.status = StavPlatby.StavPlatby.PENDING
        return True

    def markSuccessful(self):
        self.status = StavPlatby.StavPlatby.SUCCESFULL

    def markFailed(self):
        self.status = StavPlatby.StavPlatby.FAILED

    def refund(self) -> bool:
        if self.status != StavPlatby.StavPlatby.SUCCESFULL:
            return False
        self.status = StavPlatby.StavPlatby.REFUNDED
        return True

    def getStatus(self) -> StavPlatby.StavPlatby:
        return self.status
