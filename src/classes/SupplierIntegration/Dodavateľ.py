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
