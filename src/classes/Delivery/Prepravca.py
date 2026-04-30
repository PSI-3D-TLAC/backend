class Prepravca:
    id: int
    name: str

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def createShipment(self, order) -> "Zasielka":
        from Delivery import Zasielka, StavZasielky
        return Zasielka.Zasielka(0, "", StavZasielky.StavZasielky.NEODOSLANA, 0.0, "")

    def trackShipment(self, trackingNumber: str) -> str:
        return trackingNumber

    def cancelShipment(self, shipment) -> bool:
        return True

    def rename(self, newName: str):
        self.name = newName
