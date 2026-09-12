from constantes import tarjetasDebito, civicas
import random
class Tarjeta:
    def __init__(self,tipo: str):
        self.numero = 0
        self.tipo = tipo
        self.crearTarjeta(tipo)

    def crearTarjeta(self, tipo):

        if tipo == 'debito':
            lista = tarjetasDebito
        else:
            lista = civicas

        while True:
            numero = random.randint(1000000000, 9999999999)
            if numero not in lista:
                break

        self.numero = numero
        lista.append(self.numero)

