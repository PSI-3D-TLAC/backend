class TypDorucenia:
    id: int
    name: str
    price: float

    def __init__(self, id: int, name: str, price: float):
        self.id = id
        self.name = name
        self.price = price

    def updatePrice(self, newPrice: float):
        self.price = newPrice

    def rename(self, newName: str):
        self.name = newName

    def getPrice(self) -> float:
        return self.price
