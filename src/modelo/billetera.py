from modelo import Bolsillo, Tarjeta, CDT, Transaccion
from datetime import date, datetime

class Billetera:
    def __init__(self, disponible: float):
        
        self.disponible = disponible
        self.bolsillos: dict[str, Bolsillo] = {}
        self.tarjetas: list[Tarjeta] = []
        self.cdts: list[CDT] = []
        self.historial: list[Transaccion] = []

    def depositar_dinero(self, monto:float,) -> None:
        if monto <=0:
            raise ValueError("monto invalido, ingrese monto mayor que 0")
        self.disponible +=monto
        transaccion=Transaccion(monto,datetime.today().replace(microsecond=0), "depósito", "disponible")
        self.historial.append(transaccion)

    def retirar_dinero(self, monto: float) ->None:
        if monto > self.disponible:
            raise ValueError("monto invalido, dinero insuficiente en disponible")
        self.disponible -=monto
        transaccion=Transaccion(monto,datetime.today().replace(microsecond=0), "disponible", "fuera")
        self.historial.append(transaccion)

    def consultar_disponible(self) ->float:
        return self.disponible

    def consultar_historial_transacciones(self) -> list:
        return [trans for trans in self.historial]