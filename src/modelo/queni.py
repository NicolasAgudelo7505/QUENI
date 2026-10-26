import random

from .analizador_financiero import AnalizadorFinanciero
from .billetera import Billetera
from .usuario import Usuario
from .tarjeta import Civica, Tarjeta
from .excepciones import (
    MontoInvalidoError,
    OperacionNoPermitidaError,
    UsuarioDuplicadoError,
    UsuarioNoExisteError,
    CuentaNoExisteError,
    TarjetaDuplicadaError
)


class QUENI:

    def __init__(self):
        self.usuarios: dict[str, Usuario] = {}   # documento -> Usuario
        self.cuentas: dict[int, Billetera] = {}  # número de cuenta -> Billetera
        self.tarjetas: dict [str, list[int]] = {'Debito' : [], 'Civica': []}


    def generar_numero_cuenta(self) -> int:
        while True:
            numero = random.randint(1000000000, 9999999999)
            if numero not in self.cuentas:
                return numero

    def registrar_usuario(
        self, nombre: str, documento: str, sueldo: float, saldo_inicial: float = 0.0
    ) -> Usuario:
        if documento in self.usuarios:
            raise UsuarioDuplicadoError(
                f"Ya existe un usuario con el documento '{documento}'", documento=documento
            )

        if saldo_inicial < 0:
            raise MontoInvalidoError("El saldo inicial no puede ser negativo")

        numero_cuenta = self.generar_numero_cuenta()
        billetera = Billetera(numero_cuenta, saldo_inicial)
        usuario = Usuario(nombre, documento, sueldo, billetera) 

        self.usuarios[documento] = usuario
        self.cuentas[numero_cuenta] = billetera

        if saldo_inicial > 0:
            usuario.billetera.registrar_transaccion(
                monto= saldo_inicial,
                tipo= "deposito",
                destino="Disponible",
                origen="Deposito Inicial",

            )
        return usuario

    def buscar_usuario(self, documento: str) -> Usuario:
        if documento not in self.usuarios:
            raise UsuarioNoExisteError(
                f"No existe un usuario con el documento '{documento}'", documento=documento
            )
        return self.usuarios[documento]

    def buscar_cuenta(self, numero_cuenta: int) -> Billetera:
        if numero_cuenta not in self.cuentas:
            raise CuentaNoExisteError(
                f"No existe la cuenta '{numero_cuenta}'", numero_cuenta=numero_cuenta
            )
        return self.cuentas[numero_cuenta]

    def listar_usuarios(self) -> list[Usuario]:
        return list(self.usuarios.values())

    def analizador(self, documento: str) -> AnalizadorFinanciero:
        return AnalizadorFinanciero(self.buscar_usuario(documento))

    def enviar(
        self,
        documento_origen: str,
        numero_cuenta_destino: int,
        monto: float,
        bolsillo_origen: str = None,
    ) -> float:
        if monto <= 0:
            raise MontoInvalidoError("El monto debe ser positivo")

        origen = self.buscar_usuario(documento_origen).billetera
        destino = self.buscar_cuenta(numero_cuenta_destino)

        if destino is origen:
            raise OperacionNoPermitidaError("No puede enviar dinero a su propia cuenta")
        acomulado = origen.calcular_acumulado_mensual()
        impuesto = origen.impuesto.calcular(monto, acomulado)
        acumulado_actualizado = acomulado + monto

        origen.debitar(monto + impuesto, bolsillo_origen)
        destino.acreditar(monto)

        origen.registrar_transaccion(
            "envio_saliente",
            monto,
            origen=bolsillo_origen,
            destino=str(numero_cuenta_destino),
            impuesto=impuesto,
            acumulado_mensual=acumulado_actualizado,
        )
        destino.registrar_transaccion(
            "envio_entrante",
            monto,
            origen=str(origen.numero_cuenta),
        )
        return impuesto

    # ------------------------------------------------------------------
    # Tarjetas
    # ------------------------------------------------------------------

    def generar_numero_tarjeta(self, lista: list[int]) -> int:
        while True:
            numero = random.randint(1000000000, 9999999999)
            if numero not in lista:
                return numero  

    def crear_tarjeta_debito(self) -> Tarjeta:
        numero = self.generar_numero_tarjeta(self.tarjetas['Debito'])
        tarjeta = Tarjeta(numero)
        self.tarjetas['Debito'].append(tarjeta.numero)
        return tarjeta

    def crear_tarjeta_civica(self) -> Civica:
        numero = self.generar_numero_tarjeta(self.tarjetas['Civica'])
        tarjeta = Civica(numero)
        self.tarjetas['Civica'].append(tarjeta.numero)
        return tarjeta

    def asignar_tarjeta_debito(self, numero_cuenta: int) -> Tarjeta:
        billetera = self.buscar_cuenta(numero_cuenta)
        if 'Debito' in billetera.tarjetas:       
            raise TarjetaDuplicadaError("Ya existe una tarjeta débito en esta billetera", tipo="Debito")
        tarjeta = self.crear_tarjeta_debito()   
        billetera.tarjetas['Debito'] = tarjeta
        return tarjeta

    def asignar_tarjeta_civica(self, numero_cuenta: int) -> Civica:
        billetera = self.buscar_cuenta(numero_cuenta)
        if 'Civica' in billetera.tarjetas:
            raise TarjetaDuplicadaError("Ya existe una tarjeta cívica en esta billetera", tipo="Civica")
        tarjeta = self.crear_tarjeta_civica()
        billetera.tarjetas['Civica'] = tarjeta
        return tarjeta






