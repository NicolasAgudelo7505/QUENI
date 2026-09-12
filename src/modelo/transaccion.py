import datetime

class Transaccion:
    def __init__(self, monto:float, fecha: datetime, origen: str, destino:str, impuesto4x1000:float ):
        self.monto = monto
        self.fecha = fecha
        self.origen = origen
        self.destino = destino
        self.impuesto4x1000 = impuesto4x1000
