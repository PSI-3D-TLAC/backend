import StavZasielky


class Zasielka:
    id: int
    trackingNumber: str
    status: StavZasielky.StavZasielky
    shippingPrice: float
    shippedAt: str

    def __init__(self, id: int, trackingNumber: str, status: StavZasielky.StavZasielky, shippingPrice: float, shippedAt: str):
        self.id = id
        self.trackingNumber = trackingNumber
        self.status = status
        self.shippingPrice = shippingPrice
        self.shippedAt = shippedAt

    def updateStatus(self, newStatus: StavZasielky.StavZasielky):
        self.status = newStatus

    def markShipped(self, shippedAt: str):
        self.status = StavZasielky.StavZasielky.ODOSLANA
        self.shippedAt = shippedAt

    def markDelivered(self):
        self.status = StavZasielky.StavZasielky.DORUCENA

    def markFailed(self):
        self.status = StavZasielky.StavZasielky.NEDORUCENA

    def getTrackingNumber(self) -> str:
        return self.trackingNumber
