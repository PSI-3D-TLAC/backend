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

    def approve(self):
        self.status = StavZakaznickejPoziadavky.StavZakaznickejPoziadavky.APPROVED

    def reject(self):
        self.status = StavZakaznickejPoziadavky.StavZakaznickejPoziadavky.REJECTED

    def startProcessing(self):
        self.status = StavZakaznickejPoziadavky.StavZakaznickejPoziadavky.PROCESSING

    def finishProcessing(self):
        self.status = StavZakaznickejPoziadavky.StavZakaznickejPoziadavky.PROCESSED

    def updateDescription(self, newDescription: str):
        self.description = newDescription

    def getStatus(self) -> StavZakaznickejPoziadavky.StavZakaznickejPoziadavky:
        return self.status
