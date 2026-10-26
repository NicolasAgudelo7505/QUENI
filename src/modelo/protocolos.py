from typing import Protocol

from . import constantes


class Impuesto(Protocol):
    def calcular(self, monto: float, acumulado_mensual: float) -> float:
        """Devuelve el impuesto a cobrar por mover `monto`."""
        ...


class Impuesto4x1000:
    def calcular(self, monto: float, acumulado_mensual: float) -> float:
        tope_exento = constantes.TOPE_MENSUAL * constantes.VALOR_UVT
        monto_gravable = max(0, min(monto, acumulado_mensual + monto - tope_exento))
        return monto_gravable * constantes.IMPUESTO_4X1000