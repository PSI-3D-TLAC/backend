class IDeliveryService:
    def createShipment(self, order) -> "Zasielka":
        raise NotImplementedError

    def trackShipment(self, trackingNumber: str) -> str:
        raise NotImplementedError

    def cancelShipment(self, shipment) -> bool:
        raise NotImplementedError

    def updateShipmentStatus(self, shipment, status) -> bool:
        raise NotImplementedError

    def calculateShippingPrice(self, order, deliveryType) -> float:
        raise NotImplementedError
