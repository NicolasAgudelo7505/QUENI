class Tarjeta:
    def __init__(self,numero:str, tipo: str, cupoAprobado: float, cupoDisponible:float):
        self.numero = numero
        self.tipo = tipo
        self.cupoAprobado = cupoAprobado
        self.cupoDisponible = cupoDisponible
