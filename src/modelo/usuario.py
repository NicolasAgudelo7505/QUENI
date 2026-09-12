from billetera import Billetera


class Usuario:
    def __init__(self, nombre: str, documento: str, sueldo: float, billetera: Billetera):
        self.nombre = nombre
        self.documento = documento
        self.sueldo = sueldo
        self.billetera: Billetera = billetera


    def calcular_ahorro_mensual(self, bolsillo, fecha_actual=None):
            monto_calculado = bolsillo.calcular_ahorro_mensual_sugerido(fecha_actual)
            es_viable = monto_calculado <= self.sueldo
            return {"monto_sugerido": monto_calculado, "viable": es_viable}