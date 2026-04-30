class Dodavatel:
    id: int
    name: str
    address: str
    contact: str

    def __init__(self, id: int, name: str, address: str, contact: str):
        self.id = id
        self.name = name
        self.address = address
        self.contact = contact

    def supplyMaterial(self, material, quantity: int) -> bool:
        if material is None or quantity <= 0:
            return False
        material.stockQuantity = getattr(material, "stockQuantity", 0) + quantity
        return True

    def updateContact(self, newContact: str):
        self.contact = newContact

    def updateAddress(self, newAddress: str):
        self.address = newAddress

    def getContact(self) -> str:
        return self.contact

    def listSuppliedMaterials(self) -> list:
        return []
