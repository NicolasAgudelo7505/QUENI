import datetime

class Transaccion:
    def __init__(self, tipo:str,monto:float, fecha: datetime, bolsilloOrigen: str, bolsilloDestino:str, impuesto4x1000:float ):
        self.tipo = tipo
        self.monto = monto
        self.fecha = fecha
        self.bolsilloOrigen = bolsilloOrigen
        self.bolsilloDestino = bolsilloDestino
        self.impuesto4x1000 = impuesto4x1000
