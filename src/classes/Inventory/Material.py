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
