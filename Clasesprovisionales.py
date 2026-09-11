import datetime


class Usuario:
    def __init__(self, nombre:str, documento:str, sueldo:float):
        self.nombre = nombre
        self.documento = documento
        self.sueldo = sueldo

class Bolsillo:
    def __init__(self, nombre:str, saldo: float, montoMeta: float, fechaMeta: datetime):
        self.nombre = nombre
        self.saldo = saldo
        self.montoMeta = montoMeta
        self.fechaMeta = fechaMeta
        self.tasaRentabilidad: float = 0.07

class Tarjeta:
    def __init__(self,numero:str, tipo: str, cupoAprobado: float, cupoDisponible:float):
        self.numero = numero
        self.tipo = tipo
        self.cupoAprobado = cupoAprobado
        self.cupoDisponible = cupoDisponible


class CDT:
    def __init__(self, monto:float, tasaInteres: float, plazoMeses:int, fechaApertura:datetime, fechaVencimiento:datetime ):
        self.monto = monto
        self.tasaInteres = tasaInteres
        self.plazoMeses = plazoMeses
        self.fechaApertura = fechaApertura
        self.fechaVencimiento = fechaVencimiento

class Transaccion:
    def __init__(self, tipo:str,monto:float, fecha: datetime, bolsilloOrigen: str, bolsilloDestino:str, impuesto4x1000:float ):
        self.tipo = tipo
        self.monto = monto
        self.fecha = fecha
        self.bolsilloOrigen = bolsilloOrigen
        self.bolsilloDestino = bolsilloDestino
        self.impuesto4x1000 = impuesto4x1000


class Billetera:
    def __init__(self, disponible: float):
        self.disponible = disponible
        self.bolsillos:dict[str,Bolsillo] = {}
        self.tarjetas:list[Tarjeta] = []
        self.cdts:list[CDT] = []
        self.historial:list[Transaccion] = []