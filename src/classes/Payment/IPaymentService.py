class IPaymentService:
    def processPayment(self, payment) -> bool:
        raise NotImplementedError

    def refundPayment(self, payment) -> bool:
        raise NotImplementedError

    def getPaymentStatus(self, paymentId: int):
        raise NotImplementedError

    def verifyPayment(self, payment) -> bool:
        raise NotImplementedError
