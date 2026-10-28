from datetime import date

from . import constantes


class CDT:
    def __init__(
        self,
        monto: float,
        plazo_meses: int,
        fecha_apertura: date,
        fecha_vencimiento: date,
        tasa_interes: float = None,
    ):
        self.monto = monto
        self.plazo_meses = plazo_meses
        self.fecha_apertura = fecha_apertura
        self.fecha_vencimiento = fecha_vencimiento
        if tasa_interes is not None:
            self.tasa_interes = tasa_interes
        else:
            # Solo plazos válidos tienen tasa definida en TASAS_CDT.
            self.tasa_interes = constantes.TASAS_CDT[plazo_meses]

    def calcular_valor_proyectado(self) -> float:
        """Valor al vencimiento con equivalencia compuesta por días (base 365).

        valor = monto * (1 + i_EA) ** (días / 365)
        """
        dias = (self.fecha_vencimiento - self.fecha_apertura).days
        if dias <= 0:
            return self.monto
        return self.monto * (1 + self.tasa_interes) ** (dias / 365)
