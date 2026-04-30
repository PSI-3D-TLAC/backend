import StavObjednavky


class Objednavka:
    id: int
    status: StavObjednavky.StavObjednavky
    createdAt: str

    def __init__(self, id: int, status: StavObjednavky.StavObjednavky, createdAt: str):
        self.id = id
        self.status = status
        self.createdAt = createdAt
