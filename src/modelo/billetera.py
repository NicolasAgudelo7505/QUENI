from modelo import Bolsillo, Tarjeta, CDT, Transaccion, Usuario, Civica, TarjetaDebito
from datetime import date, datetime
from constantes import numeroCuentas, civicas
import random

class Billetera:
    def __init__(self, disponible: float):
        
        self.disponible = disponible
        self.bolsillos: dict[str, Bolsillo] = {}
        self.tarjetas: list[Tarjeta] = []
        self.cdts: list[CDT] = []
        self.historial: list[Transaccion] = []
        self.numeroCuenta = 0
        self.generarNumeroCuenta()


    def generarNumeroCuenta(self) -> None:
        while True:
            numero = random.randint(1000000000, 9999999999)
            if numero not in numeroCuentas:
                break
            self.numeroCuenta = numero

    def enviar(self, monto: float, destinatario: Usuario, bolsillo: str) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo")

        if bolsillo not in self.bolsillos:
            raise ValueError(f"No existe el bolsillo '{bolsillo}'")

        origen = self.bolsillos[bolsillo]

        if origen.saldo < monto:
            raise ValueError("Saldo insuficiente en el bolsillo de origen")

        origen.retirar(monto)

        billetera_destino = destinatario.billetera
        billetera_destino.disponible += monto

        transaccion = Transaccion(
            monto=monto,
            fecha=date.today(),
            origen=bolsillo
        )
        self.historial.append(transaccion)


    def depositar_dinero(self, monto:float,) -> None:
        if monto <=0:
            raise ValueError("monto invalido, ingrese monto mayor que 0")
        self.disponible +=monto
        transaccion=Transaccion(monto,datetime.today().replace(microsecond=0), "depósito", "disponible")
        self.historial.append(transaccion)

    def retirar_dinero(self, monto: float) ->None:
        if monto > self.disponible:
            raise ValueError("monto invalido, dinero insuficiente en disponible")
        self.disponible -=monto
        transaccion=Transaccion(monto,datetime.today().replace(microsecond=0), "disponible", "fuera")
        self.historial.append(transaccion)

    def consultar_disponible(self) ->float:
        return self.disponible

    def consultar_historial_transacciones(self) -> list:
        return [trans for trans in self.historial]

    def crearTarjetaDebito(self):
        tarjeta = TarjetaDebito()

    def crearTarjetaCivica(self):
        civica = Civica()

    def recargarCivica(self, monto, civica: Civica) -> None:
        if civica.numero not in civicas:
          raise ValueError(f"No existe civica con el numero '{civica.numero}'")
        else:
            civica.recargar(monto)

