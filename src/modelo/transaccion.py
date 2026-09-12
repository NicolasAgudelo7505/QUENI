import datetime

class Transaccion:
    def __init__(self, monto:float, fecha: datetime, origen: str, destino:str):
        self.monto = monto
        self.fecha = fecha
        self.origen = origen
        self.destino = destino
       
