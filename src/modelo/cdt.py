import datetime
from modelo import rentabilidad_cdt
class CDT:
    def __init__(self, monto:float, plazoMeses:int, fechaApertura:datetime, fechaVencimiento:datetime ):
        self.monto = monto
        self.tasaInteres = rentabilidad_cdt
        self.plazoMeses = plazoMeses
        self.fechaApertura = fechaApertura
        self.fechaVencimiento = fechaVencimiento