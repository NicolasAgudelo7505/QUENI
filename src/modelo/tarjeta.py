from .excepciones import MontoInvalidoError


class Tarjeta:
    def __init__(self, numero: int, fecha_expiracion: str = None, cvv: str = None):
        self.numero = numero
        self.fecha_expiracion = fecha_expiracion  # "MM/AA"
        self.cvv = cvv


class Civica(Tarjeta):
    def __init__(self, numero):
        super().__init__(numero)
        self.saldo = 0

    def recargar(self, monto: float) -> None:
        if not monto > 0:
            raise MontoInvalidoError("El monto debe ser positivo")
        self.saldo += monto