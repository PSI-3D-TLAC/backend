import StavReklamacie


class Reklamacia:
    id: int
    reason: str
    status: StavReklamacie.StavReklamacie
    createdAt: str

    def __init__(self, id: int, reason: str, status: StavReklamacie.StavReklamacie, createdAt: str):
        self.id = id
        self.reason = reason
        self.status = status
        self.createdAt = createdAt
