from datetime import date, datetime


class Transaccion:
    def __init__(
        self,
        monto: float,
        fecha: date | datetime,
        origen: str,
        destino: str,
        tipo: str,
        impuesto_4x1000: float = 0.0,
        acumulado_mensual: float = None,
        saldo_resultante: float = None,
        tasa_aplicada: float = None,
    ):
        self.monto = monto
        self.fecha = fecha
        self.origen = origen
        self.destino = destino
        self.tipo = tipo
        self.impuesto_4x1000 = impuesto_4x1000
        self.acumulado_mensual = acumulado_mensual
        self.saldo_resultante = saldo_resultante
        self.tasa_aplicada = tasa_aplicada

    def mostrar_info(self) -> str:
        info = (
            f"Fecha: {self.fecha} | Tipo: {self.tipo} | Monto: {self.monto} | "
            f"Origen: {self.origen} | Destino: {self.destino} | "
            f"Impuesto 4x1000: {self.impuesto_4x1000}"
        )
        if self.acumulado_mensual is not None:
            info += f" | Acumulado mensual: {self.acumulado_mensual}"
        if self.saldo_resultante is not None:
            info += f" | Saldo resultante: {self.saldo_resultante}"
        if self.tasa_aplicada is not None:
            info += f" | Tasa aplicada: {self.tasa_aplicada}"
        return info
