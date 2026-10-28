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
    """Bolsillo de ahorro con rentabilidad diaria (estilo Nu Cajitas).

    El interés se capitaliza de forma diferida (lazy): cada vez que se
    consulta o se mueve el saldo se aplican los días transcurridos desde
    la última capitalización. Al retirar, el saldo ya incluye lo generado.
    """

    def __init__(
        self,
        nombre: str,
        monto_meta: float = None,
        fecha_meta: date = None,
        saldo: float = 0.0,
        fecha_ultima_capitalizacion: date = None,
    ):
        self.nombre = nombre
        self.saldo = saldo
        self.monto_meta = monto_meta
        self.fecha_meta = fecha_meta
        self.tasa_rentabilidad: float = constantes.RENTABILIDAD_BOLSILLO
        # Si no se indica, arranca hoy (bolsillos nuevos o datos antiguos sin el campo).
        self.fecha_ultima_capitalizacion = fecha_ultima_capitalizacion or date.today()

    def _genera_interes(self) -> bool:
        """Los bolsillos de divisa extranjera no generan rentabilidad."""
        return self.nombre not in constantes.MONEDAS

    def capitalizar(self, fecha_actual: date = None) -> float:
        """Aplica el interés compuesto de los días transcurridos y actualiza la fecha.

        Retorna el interés generado en esta capitalización (0 si no hubo días).
        Fórmula (equivalencia diaria de la E.A.):
            saldo_nuevo = saldo * (1 + i_EA) ** (días / 365)
        """
        if fecha_actual is None:
            fecha_actual = date.today()

        # Compatibilidad con bolsillos persistidos antes de este cambio.
        if not hasattr(self, "fecha_ultima_capitalizacion") or self.fecha_ultima_capitalizacion is None:
            self.fecha_ultima_capitalizacion = fecha_actual

        if not self._genera_interes() or self.saldo <= 0:
            self.fecha_ultima_capitalizacion = fecha_actual
            return 0.0

        dias = (fecha_actual - self.fecha_ultima_capitalizacion).days
        if dias <= 0:
            return 0.0

        saldo_anterior = self.saldo
        self.saldo = saldo_anterior * (1 + self.tasa_rentabilidad) ** (dias / 365)
        self.fecha_ultima_capitalizacion = fecha_actual
        return self.saldo - saldo_anterior

    def depositar(self, monto: float) -> bool:
        if monto <= 0:
            raise MontoInvalidoError("Debe ingresar un monto mayor a 0")
        self.capitalizar()
        self.saldo += monto
        return True

    def retirar(self, monto: float) -> bool:
        if monto <= 0:
            raise MontoInvalidoError("Debe ingresar un monto mayor a 0")
        self.capitalizar()
        if monto > self.saldo:
            raise SaldoInsuficienteError(
                "Saldo insuficiente en el bolsillo",
                saldo=self.saldo,
                requerido=monto,
            )
        self.saldo -= monto
        return True

    def consultar_saldo(self, fecha_actual: date = None) -> float:
        """Saldo actualizado con la rentabilidad generada hasta la fecha dada."""
        self.capitalizar(fecha_actual)
        return self.saldo

    def calcular_rendimiento_mensual(self) -> float:
        """Estimación de rendimiento del próximo mes sobre el saldo ya capitalizado."""
        self.capitalizar()
        return (self.saldo * self.tasa_rentabilidad) / 12

    def calcular_ahorro_mensual_sugerido(self, fecha_actual: date = None) -> float:
        if fecha_actual is None:
            fecha_actual = date.today()

        if self.monto_meta is None or self.fecha_meta is None:
            raise MetaNoDefinidaError("El bolsillo no tiene una meta definida")

        self.capitalizar(fecha_actual)

        if self.saldo >= self.monto_meta:
            return 0.0

        dias_restantes = (self.fecha_meta - fecha_actual).days
        meses_restantes = math.ceil(dias_restantes / 30)

        if meses_restantes <= 0:
            raise MetaVencidaError("La fecha meta ya venció")

        monto_sugerido = (self.monto_meta - self.saldo) / meses_restantes
        return float(monto_sugerido)
