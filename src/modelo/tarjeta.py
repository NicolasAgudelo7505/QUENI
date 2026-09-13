from constantes import tarjetasDebito, civicas
import random

class Tarjeta:
    lista_numeros = []  # las hijas la sobreescriben, cada una con su lista

    def __init__(self):
        self.numero = 0
        self.crearTarjeta()

    def crearTarjeta(self):
        while True:
            numero = random.randint(1000000000, 9999999999)
            if numero not in self.lista_numeros:
                break

        self.numero = numero
        self.lista_numeros.append(self.numero)


class TarjetaDebito(Tarjeta):
    lista_numeros = tarjetasDebito  # valida y guarda contra esta lista


class Civica(Tarjeta):
    lista_numeros = civicas  # valida y guarda contra esta otra

    def __init__(self):
        super().__init__()
        self.saldo = 0

    def recargar(self, monto: float) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo")
        self.saldo += monto


