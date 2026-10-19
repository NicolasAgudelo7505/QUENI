from datetime import date

from . import constantes


class CDT:
    def __init__(self, monto: float, plazo_meses: int, fecha_apertura: date, fecha_vencimiento: date):
        self.monto = monto
        self.tasa_interes = constantes.RENTABILIDAD_CDT
        self.plazo_meses = plazo_meses
        self.fecha_apertura = fecha_apertura
        self.fecha_vencimiento = fecha_vencimiento

    def calcular_valor_proyectado(self) -> float:
        return self.monto * (1 + self.tasa_interes) ** (self.plazo_meses / 12)
