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
