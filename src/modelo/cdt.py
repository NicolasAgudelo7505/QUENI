from datetime import date, datetime
from modelo import retabilidad_cdt
class CDT:
    def __init__(self, monto:float, plazoMeses:int, fechaApertura:date, fechaVencimiento:date ):
        self.monto = monto
        self.tasaInteres = retabilidad_cdt
        self.plazoMeses = plazoMeses
        self.fechaApertura = fechaApertura
        self.fechaVencimiento = fechaVencimiento

    def calcular_valor_proyectado(self):
        return self.monto*(1+ self.tasaInteres)**(self.plazoMeses/12)



