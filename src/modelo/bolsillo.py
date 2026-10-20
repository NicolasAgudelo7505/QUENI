from datetime import date
import math

from . import constantes
from .excepciones import (
    MontoInvalidoError,
    SaldoInsuficienteError,
    MetaNoDefinidaError,
    MetaVencidaError,
)


class Bolsillo:
    def __init__(self, nombre: str, monto_meta: float = None, fecha_meta: date = None, saldo: float = 0.0):
        self.nombre = nombre
        self.saldo = saldo
        self.monto_meta = monto_meta
        self.fecha_meta = fecha_meta
        self.tasa_rentabilidad: float = constantes.RENTABILIDAD_BOLSILLO

    def depositar(self, monto: float) -> bool:
        if monto <= 0:
            raise MontoInvalidoError("Debe ingresar un monto mayor a 0")
        self.saldo += monto
        return True

    def retirar(self, monto: float) -> bool:
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
        return (self.saldo * self.tasa_rentabilidad) / 12

    def calcular_ahorro_mensual_sugerido(self, fecha_actual: date = None) -> float:
        if fecha_actual is None:
            fecha_actual = date.today()

        if self.monto_meta is None or self.fecha_meta is None:
            raise MetaNoDefinidaError("El bolsillo no tiene una meta definida")

        if self.saldo >= self.monto_meta:
            return 0.0

        dias_restantes = (self.fecha_meta - fecha_actual).days
        meses_restantes = math.ceil(dias_restantes / 30)

        if meses_restantes <= 0:
            raise MetaVencidaError("La fecha meta ya venció")

        monto_sugerido = (self.monto_meta - self.saldo) / meses_restantes
        return float(monto_sugerido)
