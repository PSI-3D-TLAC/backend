import Zamestnanec


class Sklaník(Zamestnanec.Zamestnanec):
    def __init__(self, id: int, name: str, email: str, password: str, dateOfBirht: str):
        super().__init__(id, name, email, password, dateOfBirht)

    def receiveDelivery(self, delivery) -> bool:
        return True

    def updateStock(self, material, quantity: int):
        material.stockQuantity += quantity

    def checkInventory(self, material) -> int:
        return material.stockQuantity

    def reportShortage(self, material) -> bool:
        return material.stockQuantity <= 0
