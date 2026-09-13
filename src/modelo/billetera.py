from modelo import Bolsillo, Tarjeta, CDT, Transaccion, Usuario, Civica, TarjetaDebito, MONTO_MINIMO_CDT, TIPOS_GASTO, TIPOS_INGRESO
from datetime import date, datetime, timedelta
from constantes import numeroCuentas, civicas
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
        if monto <= 0 or monto > self.disponible:
            raise ValueError("monto invalido o dinero insuficiente en disponible")
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

    def recargarCivica(self, monto: float, civica: Civica) -> None:
        if civica.numero not in civicas:
            raise ValueError(f"No existe civica con el numero '{civica.numero}'")
        else:
            civica.recargar(monto)

    def crear_bolsillo(self, nombre: str, monto_meta: float | None = None, fecha_meta: date | None = None) -> bool :
        if (monto_meta is None and fecha_meta is not None) or (monto_meta is not None and fecha_meta is None):
            raise ValueError('Monto meta y fecha meta deben ingresarse ambos juntos o ninguno')
        
        if nombre in self.bolsillos:
            raise ValueError('Ya existe un bolsillo con este nombre')

        if monto_meta <=0:
            raise ValueError('El valor del monto meta debe ser mayor a cero')

        if fecha_meta < date.today():
            raise  ValueError('La fecha meta debe ser posterior a la fecha actual')

        neuvo_bolsillo = Bolsillo(nombre, monto_meta, fecha_meta)
        self.bolsillos[nombre] = neuvo_bolsillo
        return True

    def mover_entre_bolsillos(self, bolsillo_destino: str, monto: float, bolsillo_origen:str = None) -> bool:
        if bolsillo_origen is not None and bolsillo_origen not in self.bolsillos:
            raise ValueError('El bolsillo de origen no existe')

        if bolsillo_destino not in self.bolsillos:
            raise ValueError('El bolsillo de destino no existe')
        
        if monto <=0:
            raise ValueError('El monto debe ser mayor a cero')
        
        # movimiento desde el bolsillo 
        if bolsillo_origen is not None:
            if self.bolsillos[bolsillo_origen].saldo >= monto:
                self.bolsillos[bolsillo_origen].retirar(monto)
                self.bolsillos[bolsillo_destino].depositar(monto)
            else:
                raise ValueError("Saldo insuficiente en bolsillo de origen")
            return True
        
        if self.disponible < monto:
            raise ValueError('El monto debe ser mayor al dinero en disponible y mayor que cero')
        # Movimiento desde el disponible
        self.disponible -= monto
        self.bolsillos[bolsillo_destino].depositar(monto)
        return True



    def crear_cdt(self, monto: float, plazo_meses: int, origen=None) -> bool:
        if MONTO_MINIMO_CDT > monto:
            raise ValueError(f'El monto debe ser mayor que el monto mínimo del cdt: {MONTO_MINIMO_CDT} ')

        if plazo_meses <=0:
            raise ValueError('El plazo de los meses debe ser mayor que cero')
        
        fecha_apertura = date.today()
        fecha_vencimiento =  fecha_apertura + timedelta(days=30 * plazo_meses)
        
        if origen is not None:
            if origen not in self.bolsillos:
                raise ValueError('El bolsillo ingresado no existe')
            
            if self.bolsillos[origen].saldo < monto:
                raise ValueError('Saldo insuficiente del origen')
            
            self.bolsillos[origen].retirar(monto)
            self.cdts.append(CDT(monto, plazo_meses, fecha_apertura, fecha_vencimiento ))
            return True

        if self.disponible < monto:
            raise ValueError('Saldo insuficiente en el origen')
        self.disponible -= monto
        cdt = CDT(monto, plazo_meses, fecha_apertura, fecha_vencimiento )
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
                    resultados[nombre_bolsillo] = usuario.calcular_ahorro_mensual(bolsillo, fecha_actual)
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
                gastos_por_mes[clave_mes] = gastos_por_mes.get(clave_mes, 0.0) + transaccion.monto
            elif transaccion.tipo in TIPOS_INGRESO:
                ingresos_por_mes[clave_mes] = ingresos_por_mes.get(clave_mes, 0.0) + transaccion.monto

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
            "alerta_riesgo": alerta_riesgo
        }