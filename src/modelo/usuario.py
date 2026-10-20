from .billetera import Billetera
from .excepciones import MontoInvalidoError


class Usuario:
    """Datos de la persona y su billetera. No tiene lógica de negocio."""

    def __init__(self, nombre: str, documento: str, sueldo: float, billetera: Billetera):
        if sueldo <= 0:
            raise MontoInvalidoError("El sueldo debe ser mayor a cero")
        self.nombre = nombre
        self.documento = documento
        self.sueldo = sueldo
        self.billetera: Billetera = billetera
