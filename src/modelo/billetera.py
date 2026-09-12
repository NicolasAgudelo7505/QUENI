from usuario import Usuario
from cdt import CDT
from bolsillo import Bolsillo
from tarjeta import  Tarjeta
from transaccion import Transaccion


class Billetera:
    def __init__(self, disponible: float):
        self.disponible = disponible
        self.bolsillos:dict[str,Bolsillo] = {}
        self.tarjetas:list[Tarjeta] = []
        self.cdts:list[CDT] = []
        self.historial:list[Transaccion] = []