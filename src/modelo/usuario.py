from billetera import Billetera 
class Usuario:
    def __init__(self, nombre:str, documento:str, sueldo:float):
        self.nombre = nombre
        self.documento = documento
        self.sueldo = sueldo
        self.billetera : Billetera = None 
