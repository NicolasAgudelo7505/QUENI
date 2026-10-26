from datetime import date, datetime, timedelta

from . import constantes
from .bolsillo import Bolsillo
from .cdt import CDT
from .tarjeta import Tarjeta, Civica
from .transaccion import Transaccion
from .excepciones import (
    MontoInvalidoError,
    SaldoInsuficienteError,
    BolsilloNoExisteError,
    BolsilloDuplicadoError,
    MetaInvalidaError,
    CDTInvalidoError,
    DivisaNoSoportadaError,
    OperacionNoPermitidaError,
    TarjetaNoExisteError,
)
from .protocolos import Impuesto, Impuesto4x1000


class Billetera:
    """Maneja el dinero de UN solo usuario: disponible, bolsillos, CDTs,
    tarjetas e historial. No conoce a Usuario ni a QUENI."""

    def __init__(self, numero_cuenta: int, disponible: float = 0.0, impuesto: Impuesto | None = None):
        self.numero_cuenta = numero_cuenta
        self.disponible = disponible
        self.bolsillos: dict[str, Bolsillo] = {}
        self.tarjetas: dict[str,Tarjeta] = {}
        self.cdts: list[CDT] = []
        self.historial: list[Transaccion] = []
        self.impuesto = impuesto if impuesto is not None else Impuesto4x1000()

    # ------------------------------------------------------------------
    # Operaciones básicas reutilizables
    # ------------------------------------------------------------------

    def registrar_transaccion(
        self,
        tipo: str,
        monto: float,
        origen: str = None,
        destino: str = None,
        impuesto: float = 0.0,
        acumulado_mensual: float = None,
        tasa_aplicada: float = None,
    ) -> Transaccion:
        transaccion = Transaccion(
            monto=monto,
            fecha=datetime.now().replace(microsecond=0),
            origen=origen,
            destino=destino,
            tipo=tipo,
            impuesto_4x1000=impuesto,
            acumulado_mensual=acumulado_mensual,
            saldo_resultante=self.disponible,
            tasa_aplicada=tasa_aplicada,
        )
        self.historial.append(transaccion)
        return transaccion

    def debitar(self, monto: float, origen: str = None) -> None:
        """Descuenta dinero del disponible (origen=None) o de un bolsillo.
        Valida todo antes de tocar cualquier saldo."""
        if monto <= 0:
            raise MontoInvalidoError()

        if origen is None:
            if self.disponible < monto:
                raise SaldoInsuficienteError(
                    "Saldo insuficiente en el disponible",
                    saldo=self.disponible,
                    requerido=monto,
                )
            self.disponible -= monto
        else:
            if origen not in self.bolsillos:
                raise BolsilloNoExisteError(f"No existe el bolsillo '{origen}'", nombre=origen)
            self.bolsillos[origen].retirar(monto)  # Bolsillo.retirar ya valida el saldo

    def acreditar(self, monto: float) -> None:
        if monto <= 0:
            raise MontoInvalidoError()
        self.disponible += monto

    # ------------------------------------------------------------------
    # 4x1000
    # ------------------------------------------------------------------

    def calcular_acumulado_mensual(self) -> float:
        """Suma de retiros y envíos del mes en curso (antes de la operación actual)."""
        hoy = date.today()
        acumulado = 0.0
        for transaccion in self.historial:
            if transaccion.fecha.month == hoy.month and transaccion.fecha.year == hoy.year:
                if transaccion.tipo in constantes.TIPOS_COBRO_4X1000:
                    acumulado += transaccion.monto
        return acumulado


    # ------------------------------------------------------------------
    # Depósitos y retiros
    # ------------------------------------------------------------------

    def depositar_dinero(self, monto: float, destino: str = None) -> None:
        if monto <= 0:
            raise MontoInvalidoError("monto invalido, ingrese monto mayor que 0")

        if destino is None:
            self.disponible += monto
        else:
            if destino not in self.bolsillos:
                raise BolsilloNoExisteError(f"No existe el bolsillo '{destino}'", nombre=destino)
            self.bolsillos[destino].depositar(monto)

        self.registrar_transaccion("deposito", monto, destino=destino)

    def retirar_dinero(self, monto: float, origen: str = None) -> None:
        if monto <= 0:
            raise MontoInvalidoError("El monto inválido, debe ser mayor a cero")
        acomulado = self.calcular_acumulado_mensual()
        impuesto = self.impuesto.calcular(monto, acomulado)
        acumulado_actualizado = acomulado + monto

        self.debitar(monto + impuesto, origen)

        self.registrar_transaccion(
            "retiro",
            monto,
            origen=origen,
            destino="fuera",
            impuesto=impuesto,
            acumulado_mensual=acumulado_actualizado,
        )

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def consultar_disponible(self) -> float:
        return self.disponible

    def consultar_historial_transacciones(self) -> list[str]:
        return [transaccion.mostrar_info() for transaccion in self.historial]

    # ------------------------------------------------------------------
    # Bolsillos
    # ------------------------------------------------------------------

    def crear_bolsillo(
        self,
        nombre: str,
        monto_meta: float | None = None,
        fecha_meta: date | None = None,
    ) -> bool:
        if (monto_meta is None and fecha_meta is not None) or (
            monto_meta is not None and fecha_meta is None
        ):
            raise MetaInvalidaError(
                "Monto meta y fecha meta deben ingresarse ambos juntos o ninguno"
            )

        if nombre in self.bolsillos:
            raise BolsilloDuplicadoError("Ya existe un bolsillo con este nombre", nombre=nombre)

        if monto_meta is not None and monto_meta <= 0:
            raise MetaInvalidaError("El valor del monto meta debe ser mayor a cero")

        if fecha_meta is not None and fecha_meta <= date.today():
            raise MetaInvalidaError("La fecha meta debe ser posterior a la fecha actual")

        self.bolsillos[nombre] = Bolsillo(
            nombre=nombre,
            monto_meta=monto_meta,
            fecha_meta=fecha_meta,
        )
        return True

    def mover_entre_bolsillos(
        self, bolsillo_destino: str, monto: float, bolsillo_origen: str = None
    ) -> bool:
        if bolsillo_destino in constantes.MONEDAS or (
            bolsillo_origen is not None and bolsillo_origen in constantes.MONEDAS
        ):
            raise OperacionNoPermitidaError(
                "Use el método cambiar_divisas para interactuar con bolsillos de moneda extranjera"
            )

        if bolsillo_origen is not None and bolsillo_origen not in self.bolsillos:
            raise BolsilloNoExisteError("El bolsillo de origen no existe", nombre=bolsillo_origen)

        if bolsillo_destino not in self.bolsillos:
            raise BolsilloNoExisteError("El bolsillo de destino no existe", nombre=bolsillo_destino)

        if monto <= 0:
            raise MontoInvalidoError("El monto debe ser mayor a cero")

        self.debitar(monto, bolsillo_origen)
        self.bolsillos[bolsillo_destino].depositar(monto)

        self.registrar_transaccion(
            "movimiento_bolsillos",
            monto,
            origen=bolsillo_origen,
            destino=bolsillo_destino,
        )
        return True

    # ------------------------------------------------------------------
    # CDT
    # ------------------------------------------------------------------

    def crear_cdt(self, monto: float, plazo_meses: int, origen: str = None) -> bool:
        if monto < constantes.MONTO_MINIMO_CDT:
            raise CDTInvalidoError(
                f"El monto debe ser mayor que el monto mínimo del cdt: {constantes.MONTO_MINIMO_CDT}"
            )

        if plazo_meses <= 0:
            raise CDTInvalidoError("El plazo de los meses debe ser mayor que cero")

        fecha_apertura = date.today()
        fecha_vencimiento = fecha_apertura + timedelta(days=30 * plazo_meses)

        # Primero se debita (puede fallar); solo después se crea el CDT.
        self.debitar(monto, origen)

        self.cdts.append(
            CDT(
                monto=monto,
                plazo_meses=plazo_meses,
                fecha_apertura=fecha_apertura,
                fecha_vencimiento=fecha_vencimiento,
            )
        )

        self.registrar_transaccion(
            "apertura_cdt",
            monto,
            origen=origen,
            destino="cdt",
        )
        return True

    def redimir_cdt(self, cdt: CDT) -> bool:
        fecha = date.today()
        if cdt not in self.cdts:
            raise CDTInvalidoError("El CDT no pertenece a esta billetera o ya fue redimido")

        if fecha < cdt.fecha_vencimiento:
            raise OperacionNoPermitidaError("El CDT aún no ha vencido")

        valor_final = cdt.calcular_valor_proyectado()
        valor_generado = valor_final - cdt.monto
        self.acreditar(valor_final)
        self.cdts.remove(cdt)

        self.registrar_transaccion(
            "cobro_cdt",
            valor_generado,
            origen="cdt",
            destino="disponible",
                                   )
        return True

    # ------------------------------------------------------------------
    # Divisas
    # ------------------------------------------------------------------

    def cambiar_divisas(
            self, monto: float, tipo_divisa: tuple[str, str], origen: str = None
    ) -> bool:
        if monto <= 0:
            raise MontoInvalidoError("El monto debe ser mayor a cero")

        if tipo_divisa not in constantes.TASAS_DE_CAMBIO:
            raise DivisaNoSoportadaError("La tasa de cambio es incorrecta", par=tipo_divisa)

        moneda_origen, moneda_destino = tipo_divisa
        tasa = constantes.TASAS_DE_CAMBIO[tipo_divisa]
        monto_convertido = monto * tasa

        # El origen tiene que coincidir con la moneda que se quiere cambiar.
        if moneda_origen == "COP":
            if origen in constantes.MONEDAS:
                raise OperacionNoPermitidaError(
                    "Para cambiar desde COP use el disponible o un bolsillo normal"
                )
        elif origen != moneda_origen:
            raise OperacionNoPermitidaError(
                f"Para cambiar desde {moneda_origen} debe usar el bolsillo '{moneda_origen}'"
            )

        # Primero se debita (puede fallar); solo después se acredita el destino.
        self.debitar(monto, origen)

        if moneda_destino == "COP":
            self.acreditar(monto_convertido)  # los pesos vuelven al disponible
        else:
            if moneda_destino not in self.bolsillos:
                self.crear_bolsillo(nombre=moneda_destino)
            self.bolsillos[moneda_destino].depositar(monto_convertido)

        self.registrar_transaccion(
            "cambio_divisa",
            monto,
            origen=origen,
            destino="disponible" if moneda_destino == "COP" else moneda_destino,
            tasa_aplicada=tasa,
        )
        return True

    # ------------------------------------------------------------------
    # Tarjetas
    # ------------------------------------------------------------------

    def recargar_civica(self, monto: float, civica: Civica, origen: str = None) -> None:
        if civica is None or self.tarjetas.get('Civica') is not civica:
            numero = getattr(civica, 'numero', None)
            raise TarjetaNoExisteError(
                f"No existe civica con el numero '{numero}' en esta billetera",
                numero=numero,
            )

        self.debitar(monto, origen)
        civica.recargar(monto)

        self.registrar_transaccion(
            "recarga_civica",
            monto,
            origen=origen,
            destino=str(civica.numero),
        )

