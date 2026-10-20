from .excepciones import MontoInvalidoError

class Tarjeta:
    def __init__(self, numero: int):
        self.numero = numero

class Civica(Tarjeta):
    def __init__(self, numero):
        super().__init__(numero)
        self.saldo = 0

    def recargar(self, monto: float) -> None:
        if monto <= 0:
            raise MontoInvalidoError("El monto debe ser positivo")
        self.saldo += monto