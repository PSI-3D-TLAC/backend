class Model3D:
    id: int
    name: str
    filePath: str
    volume: float
    size: float

    def __init__(self, id: int, name: str, filePath: str, volume: float, size: float):
        self.id = id
        self.name = name
        self.filePath = filePath
        self.volume = volume
        self.size = size

    def getVolume(self) -> float:
        return self.volume

    def getSize(self) -> float:
        return self.size

    def updateFile(self, newFilePath: str):
        self.filePath = newFilePath

    def rename(self, newName: str):
        self.name = newName
