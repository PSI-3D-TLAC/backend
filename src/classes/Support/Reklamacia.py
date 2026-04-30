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

    def review(self):
        self.status = StavReklamacie.StavReklamacie.UNDER_REVIEW

    def approve(self):
        self.status = StavReklamacie.StavReklamacie.APPROVED

    def reject(self):
        self.status = StavReklamacie.StavReklamacie.REJECETED

    def updateReason(self, newReason: str):
        self.reason = newReason

    def getStatus(self) -> StavReklamacie.StavReklamacie:
        return self.status
