class Material:
    id: int
    name: str
    type: str
    color: str
    description: str
    stockQuantity: int

    def __init__(self, id: int, name: str, type: str, color: str, description: str, stockQuantity: int):
        self.id = id
        self.name = name
        self.type = type
        self.color = color
        self.description = description
        self.stockQuantity = stockQuantity

    def addStock(self, quantity: int):
        self.stockQuantity += quantity

    def removeStock(self, quantity: int) -> bool:
        if quantity > self.stockQuantity:
            return False
        self.stockQuantity -= quantity
        return True

    def isAvailable(self, quantity: int = 1) -> bool:
        return self.stockQuantity >= quantity

    def updateDescription(self, newDescription: str):
        self.description = newDescription
