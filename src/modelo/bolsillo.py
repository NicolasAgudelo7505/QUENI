from datetime import date, datetime
from .constantes import RENTABILIDAD_BOLSILLO
from .excepciones import (  # NUEVO
    MontoInvalidoError,
    SaldoInsuficienteError,
    MetaNoDefinidaError,
    MetaVencidaError,
)
import math


class Bolsillo:
    def __init__(self, nombre: str, monto_meta: float = None, fecha_meta: datetime = None, saldo: float = 0.0):
        self.nombre = nombre
        self.saldo = saldo
        self.monto_meta = monto_meta
        self.fecha_meta = fecha_meta
        self.tasaRentabilidad: float = RENTABILIDAD_BOLSILLO

    def depositar(self, monto) -> bool | ValueError:
        if monto > 0:
            self.saldo += monto
            return True
        else:
            raise MontoInvalidoError("Debe ingresar un monto mayor a 0")  # CAMBIO

    def retirar(self, monto) -> bool | ValueError:
        # CAMBIO: antes ambos casos lanzaban el mismo mensaje ("Debe ingresar
        # un monto mayor a 0"), aun cuando el problema era saldo insuficiente.
        # Ahora cada situación tiene su propia excepción.
        if monto <= 0:
            raise MontoInvalidoError("Debe ingresar un monto mayor a 0")
        if monto > self.saldo:
            raise SaldoInsuficienteError(
                "Saldo insuficiente en el bolsillo",
                saldo=self.saldo,
                requerido=monto,
            )
        self.saldo -= monto
        return True

    def calcular_rendimiento_mensual(self) -> float:
        return (self.saldo * self.tasaRentabilidad) / 12
    
    def calcular_ahorro_mensual_sugerido(self, fecha_actual=None):
        if fecha_actual is None:
            fecha_actual = date.today()

        if self.monto_meta is None or self.fecha_meta is None:
            raise MetaNoDefinidaError("El bolsillo no tiene una meta definida")  # CAMBIO
        
        if self.saldo >= self.monto_meta:
            return 0.0
        
        dias_restantes = (self.fecha_meta - fecha_actual).days
        meses_restantes = math.ceil(dias_restantes / 30)

        if meses_restantes <= 0:
            raise MetaVencidaError("La fecha meta ya venció")  # CAMBIO
        monto_sugerido = (self.monto_meta - self.saldo) / meses_restantes

        return float(monto_sugerido)