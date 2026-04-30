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
