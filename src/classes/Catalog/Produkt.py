class Produkt:
    id: int
    name: str
    description: str
    price: float
    isActive: bool

    def __init__(self, id: int, name: str, description: str, price: float, isActive: bool):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.isActive = isActive

    def activate(self):
        self.isActive = True

    def deactivate(self):
        self.isActive = False

    def updatePrice(self, newPrice: float):
        self.price = newPrice

    def updateDescription(self, newDescription: str):
        self.description = newDescription

    def getInfo(self) -> str:
        return f"{self.name} ({self.id}): {self.price}"
