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
