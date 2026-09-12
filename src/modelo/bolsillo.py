from datetime import date, datetime
from modelo import rentabilidadBolsillo
import math


class Bolsillo:
    def __init__(self, nombre: str, montoMeta: float = None, fechaMeta: datetime = None, saldo: float = 0.0):
        self.nombre = nombre
        self.saldo = saldo
        self.montoMeta = montoMeta
        self.fechaMeta = fechaMeta
        self.tasaRentabilidad: float = rentabilidadBolsillo

    def depositar(self, monto) -> bool | ValueError:
        if monto > 0:
            self.saldo += monto
            return "Depósito exitoso"
        else:
            raise ValueError("Debe ingresar un monto mayor a 0")

    def retirar(self, monto) -> bool | ValueError:
        if monto > 0 and monto <= self.saldo:
            self.saldo -= monto
            return "Depósito exitoso"
        else:
            raise ValueError("Debe ingresar un monto mayor a 0")

    def calcular_rendimiento_mensual(self) -> float:
        return (self.saldo * rentabilidadBolsillo) / 12
    
    def calcular_ahorro_mensual_sugerido(self, fecha_actual=None):
        if fecha_actual is None:
            fecha_actual = date.today()

        if self.monto_meta is None or self.fecha_meta is None:
            raise ValueError("El bolsillo no tiene una meta definida")
        
        if self.saldo >= self.monto_meta:
            return 0.0
        
        dias_restantes = (self.fecha_meta - fecha_actual).days
        meses_restantes = math.ceil(dias_restantes / 30)

        if meses_restantes <= 0:
            raise ValueError("La fecha meta ya venció")
        monto_sugerido = (self.monto_meta - self.saldo) / meses_restantes

        return float(monto_sugerido)
