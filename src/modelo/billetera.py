from modelo import (
    Bolsillo,
    Tarjeta,
    CDT,
    Transaccion,
    Usuario,
    Civica,
    TarjetaDebito,
    MONTO_MINIMO_CDT,
    TIPOS_GASTO,
    TIPOS_INGRESO,
    tarjetasDebito,
    civicas,
    TASAS_DE_CAMBIO,
    numeroCuentas,
    VALOR_UVT,
    IMPUESTO_4X1000,
    TOPE_MENSUAL
)

from datetime import date, datetime, timedelta
import random
import statistics


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

    def calcular_4x1000(self, monto: float) -> float:
        hoy = date.today()

        acumulado_mensual = 0.0
        TIPOS_COBRO = [
            "retiro",
            "envio_saliente",
        ]  

        for transaccion in self.historial:
            if (transaccion.fecha.month == hoy.month and transaccion.fecha.year == hoy.year):
                if transaccion.tipo in TIPOS_COBRO:
                    acumulado_mensual += transaccion.monto

        tope_exento = TOPE_MENSUAL * VALOR_UVT

        if acumulado_mensual >= tope_exento:
            return monto * IMPUESTO_4X1000 

        if (acumulado_mensual + monto) > tope_exento:
            monto_gravable = (acumulado_mensual + monto) - tope_exento
            return monto_gravable * IMPUESTO_4X1000
        return 0.0

    def enviar(self, monto: float, destinatario: Usuario, origen: str = None) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser positivo")

        impuesto = self._calcular_4x1000(monto)
        total_a_descontar = monto + impuesto

        if origen is not None:
            if origen not in self.bolsillos:
                raise ValueError(f"No existe el bolsillo '{origen}'")
            if self.bolsillos[origen].saldo < total_a_descontar:
                raise ValueError("Saldo insuficiente en el bolsillo para el envío y el 4x1000")
            
            self.bolsillos[origen].retirar(total_a_descontar)
        else:
            if self.disponible < total_a_descontar:
                raise ValueError("Saldo insuficiente en el disponible para el envío y el 4x1000")
            
            self.disponible -= total_a_descontar

        # Entregar al DESTINATARIO
        billetera_destino = destinatario.billetera
        billetera_destino.disponible += monto 

        hoy = date.today()

        transaccion_salida = Transaccion(
            monto=monto, 
            fecha=hoy, 
            origen=origen,
            destino=None,
            tipo="envio_saliente", 
            impuesto_4x1000=impuesto 
        )
        self.historial.append(transaccion_salida)

        transaccion_entrada = Transaccion(
            monto=monto, 
            fecha=hoy,
            origen=None,
            destino=None, 
            tipo="envio_entrante", 
            impuesto_4x1000=0.0
        )
        billetera_destino.historial.append(transaccion_entrada)

    def depositar_dinero(
        self,
        monto: float,
    ) -> None:
        if monto <= 0:
            raise ValueError("monto invalido, ingrese monto mayor que 0")
        self.disponible += monto
        transaccion = Transaccion(
            monto, datetime.today().replace(microsecond=0), "depósito", "disponible"
        )
        self.historial.append(transaccion)

    def retirar_dinero(self, monto: float) -> None:
        if monto <= 0:
            raise ValueError("El monto inválido, debe ser mayor a cero")
            
        impuesto = self._calcular_4x1000(monto)
        total_a_descontar = monto + impuesto

        if self.disponible < total_a_descontar:
            raise ValueError("Dinero insuficiente en disponible para cubrir el retiro y el 4x1000")
            
        self.disponible -= total_a_descontar
        
        transaccion = Transaccion(
            monto=monto, 
            fecha=datetime.today().replace(microsecond=0), 
            origen=None, 
            destino="fuera", 
            tipo="retiro", 
            impuesto_4x1000=impuesto
        )
        self.historial.append(transaccion)

    def consultar_disponible(self) -> float:
        return self.disponible

    def consultar_historial_transacciones(self) -> list[str]:
        return [transaccion.mostrar_info() for transaccion in self.historial]

    def crearTarjetaDebito(self):
        tarjeta = TarjetaDebito()

    def crearTarjetaCivica(self):
        civica = Civica()

    def recargarCivica(self, monto: float, civica: Civica) -> None:
        if civica.numero not in civicas:
            raise ValueError(f"No existe civica con el numero '{civica.numero}'")
        else:
            civica.recargar(monto)

    def crear_bolsillo(
        self,
        nombre: str,
        monto_meta: float | None = None,
        fecha_meta: date | None = None,
    ) -> bool:
        if (monto_meta is None and fecha_meta is not None) or (
            monto_meta is not None and fecha_meta is None
        ):
            raise ValueError(
                "Monto meta y fecha meta deben ingresarse ambos juntos o ninguno"
            )

        if nombre in self.bolsillos:
            raise ValueError("Ya existe un bolsillo con este nombre")

        if monto_meta is not None and monto_meta <= 0:
            raise ValueError("El valor del monto meta debe ser mayor a cero")

        if fecha_meta is not None and fecha_meta <= date.today():
            raise ValueError("La fecha meta debe ser posterior a la fecha actual")

        nuevo_bolsillo = Bolsillo(nombre, monto_meta, fecha_meta)
        self.bolsillos[nombre] = nuevo_bolsillo

        return True

    def mover_entre_bolsillos(
        self, bolsillo_destino: str, monto: float, bolsillo_origen: str = None
    ) -> bool:
        divisas = ["USD", "COP", "EUR"]
        if bolsillo_destino in divisas or (
            bolsillo_origen is not None and bolsillo_origen in divisas
        ):
            raise ValueError(
                "Use el método cambiar_divisas para interactuar con bolsillos de moneda extranjera"
            )

        if bolsillo_origen is not None and bolsillo_origen not in self.bolsillos:
            raise ValueError("El bolsillo de origen no existe")

        if bolsillo_destino not in self.bolsillos:
            raise ValueError("El bolsillo de destino no existe")

        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        # movimiento desde el bolsillo
        if bolsillo_origen is not None:
            if self.bolsillos[bolsillo_origen].saldo >= monto:
                self.bolsillos[bolsillo_origen].retirar(monto)
                self.bolsillos[bolsillo_destino].depositar(monto)
            else:
                raise ValueError("Saldo insuficiente en bolsillo de origen")
            return True

        if self.disponible < monto:
            raise ValueError(
                "El monto debe ser mayor al dinero en disponible y mayor que cero"
            )
        # Movimiento desde el disponible
        self.disponible -= monto
        self.bolsillos[bolsillo_destino].depositar(monto)
        return True

    def crear_cdt(self, monto: float, plazo_meses: int, origen=None) -> bool:
        if MONTO_MINIMO_CDT > monto:
            raise ValueError(f"El monto debe ser mayor que el monto mínimo del cdt: {MONTO_MINIMO_CDT} ")

        if plazo_meses <= 0:
            raise ValueError("El plazo de los meses debe ser mayor que cero")

        fecha_apertura = date.today()
        fecha_vencimiento = fecha_apertura + timedelta(days=30 * plazo_meses)

        if origen is not None:
            if origen not in self.bolsillos:
                raise ValueError("El bolsillo ingresado no existe")

            if self.bolsillos[origen].saldo < monto:
                raise ValueError("Saldo insuficiente del origen")

            self.bolsillos[origen].retirar(monto)
            self.cdts.append(CDT(monto, plazo_meses, fecha_apertura, fecha_vencimiento))
            return True

        if self.disponible < monto:
            raise ValueError("Saldo insuficiente en el origen")
        self.disponible -= monto
        cdt = CDT(monto, plazo_meses, fecha_apertura, fecha_vencimiento)
        self.cdts.append(cdt)

        return True

    # TODO revisar
    def calcular_ahorro_mensual_sugerido(self, usuario, fecha_actual=None):
        if fecha_actual is None:
            fecha_actual = date.today()
        resultados = {}

        for nombre_bolsillo, bolsillo in self.bolsillos.items():
            if bolsillo.monto_meta is not None:
                try:
                    resultados[nombre_bolsillo] = usuario.calcular_ahorro_mensual(
                        bolsillo, fecha_actual
                    )
                except ValueError as error:
                    resultados[nombre_bolsillo] = {"error": str(error)}
        return resultados

    # TODO revisar
    def predecir_gastos_e_ingresos(self, fecha_actual=None) -> bool:
        if fecha_actual is None:
            fecha_actual = date.today()
        mes_actual = fecha_actual.month
        año_actual = fecha_actual.year

        gastos_por_mes = {}
        ingresos_por_mes = {}
        meses_registrados = set()

        for transaccion in self.historial:
            t_mes = transaccion.fecha.month
            t_año = transaccion.fecha.year

            if t_año == año_actual and t_mes == mes_actual:
                continue

            clave_mes = (t_año, t_mes)
            meses_registrados.add(clave_mes)

            if transaccion.tipo in TIPOS_GASTO:
                gastos_por_mes[clave_mes] = (
                    gastos_por_mes.get(clave_mes, 0.0) + transaccion.monto
                )
            elif transaccion.tipo in TIPOS_INGRESO:
                ingresos_por_mes[clave_mes] = (
                    ingresos_por_mes.get(clave_mes, 0.0) + transaccion.monto
                )

        if len(meses_registrados) < 1:
            return {"suficiente_historial": False}

        # Calcular promedios
        lista_gastos = [gastos_por_mes.get(mes, 0.0) for mes in meses_registrados]
        lista_ingresos = [ingresos_por_mes.get(mes, 0.0) for mes in meses_registrados]

        gasto_proyectado = statistics.mean(lista_gastos)
        ingreso_proyectado = statistics.mean(lista_ingresos)

        # Proyecciones financieras
        saldo_proyectado = self.disponible + ingreso_proyectado - gasto_proyectado
        alerta_riesgo = gasto_proyectado > ingreso_proyectado

        return {
            "suficiente_historial": True,
            "gasto_estimado": float(gasto_proyectado),
            "ingreso_estimado": float(ingreso_proyectado),
            "saldo_proyectado": float(saldo_proyectado),
            "alerta_riesgo": alerta_riesgo,
        }


    def cambiar_divisas(
        self, monto: float, tipo_divisa: tuple[str, str], origen: str = None) -> bool:
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a cero")

        if tipo_divisa not in TASAS_DE_CAMBIO:
            raise ValueError("La tasa de cambio es incorrecta")

        moneda_destino = tipo_divisa[1]

        # dinero de bolsillo
        if moneda_destino not in self.bolsillos:
            self.crear_bolsillo(moneda_destino)

        monto_convertido = monto * TASAS_DE_CAMBIO[tipo_divisa]

        if origen is not None:
            if origen not in self.bolsillos:
                raise ValueError("El origen no existe")

            if self.bolsillos[origen].saldo < monto:
                raise ValueError("Saldo insuficiente del origen")

            self.bolsillos[origen].retirar(monto)
            self.bolsillos[moneda_destino].depositar(monto_convertido)

        # dinero de disponible
        else:
            if self.disponible < monto:
                raise ValueError("Saldo del origen insuficiente")

            self.disponible -= monto
            self.bolsillos[moneda_destino].depositar(monto_convertido)

        nueva_transaccion = Transaccion(
            monto=monto,
            fecha=date.today(),
            origen=origen,
            destino=moneda_destino,
            tipo="cambio_divisa",
            impuesto_4x1000=0,
        )
        self.historial.append(nueva_transaccion)
        return True
