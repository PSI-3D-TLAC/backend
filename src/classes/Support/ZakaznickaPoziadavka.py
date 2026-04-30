import StavZakaznickejPoziadavky


class ZakaznickaPoziadavka:
    id: int
    type: str
    description: str
    status: StavZakaznickejPoziadavky.StavZakaznickejPoziadavky

    def __init__(self, id: int, type: str, description: str, status: StavZakaznickejPoziadavky.StavZakaznickejPoziadavky):
        self.id = id
        self.type = type
        self.description = description
        self.status = status
