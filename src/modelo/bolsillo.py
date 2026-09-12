import datetime
from modelo import rentabilidad_bolsillo

class Bolsillo:
    def __init__(self, nombre:str, saldo: float, montoMeta: float, fechaMeta: datetime):
        self.nombre = nombre
        self.saldo = saldo
        self.montoMeta = montoMeta
        self.fechaMeta = fechaMeta
        self.tasaRentabilidad: float = rentabilidad_bolsillo