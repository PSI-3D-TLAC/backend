class IInventoryService:
    def addMaterial(self, material) -> bool:
        raise NotImplementedError

    def removeMaterial(self, materialId: int) -> bool:
        raise NotImplementedError

    def getStock(self, materialId: int) -> int:
        raise NotImplementedError

    def updateStock(self, materialId: int, quantity: int) -> bool:
        raise NotImplementedError

    def listMaterials(self) -> list:
        raise NotImplementedError

    def reserveMaterial(self, materialId: int, quantity: int) -> bool:
        raise NotImplementedError
