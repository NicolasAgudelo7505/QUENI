import datetime

class Transaccion:
    def __init__(self, monto:float, fecha: datetime, origen: str, destino:str, tipo:str, impuesto_4x1000):
        self.monto = monto
        self.fecha = fecha
        self.origen = origen
        self.destino = destino
        self.tipo = tipo
        self.impuesto_4x1000 = impuesto_4x1000

    def mostrar_info(self) -> str:
        return f'Fecha de transacción: {self.fecha} | Monto: {self.monto} | Tipo:{self.tipo} |Origen: {self.origen} | Destino {self.destino} | Impuesto 4x1000 {self.impuesto_4x1000}'

