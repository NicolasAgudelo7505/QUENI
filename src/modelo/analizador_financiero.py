from datetime import date, datetime
import statistics

from . import constantes
from .excepciones import BilleteraError, BolsilloNoExisteError
from .usuario import Usuario


class AnalizadorFinanciero:
    """Analiza el historial y los bolsillos de un usuario.
    Solo LEE: nunca modifica saldos ni el historial."""

    def __init__(self, usuario: Usuario):
        self.usuario = usuario
        self.billetera = usuario.billetera

    def _a_fecha(self, fecha) -> date:
        # El historial puede tener date o datetime; se unifica a date para comparar.
        if isinstance(fecha, datetime):
            return fecha.date()
        return fecha

    # ------------------------------------------------------------------
    # Ahorro mensual sugerido
    # ------------------------------------------------------------------

    def ahorro_de_bolsillo(self, nombre_bolsillo: str, fecha_actual: date = None) -> dict:
        """Ahorro sugerido de UN bolsillo. Si el bolsillo no tiene meta o la
        meta venció, deja subir la excepción."""
        if nombre_bolsillo not in self.billetera.bolsillos:
            raise BolsilloNoExisteError(f"No existe el bolsillo '{nombre_bolsillo}'", nombre=nombre_bolsillo)

        bolsillo = self.billetera.bolsillos[nombre_bolsillo]
        monto_sugerido = bolsillo.calcular_ahorro_mensual_sugerido(fecha_actual)
        return {
            "monto_sugerido": monto_sugerido,
            "viable": monto_sugerido <= self.usuario.sueldo,
        }

    def ahorro_mensual_sugerido(self, fecha_actual: date = None) -> dict:
        """Ahorro sugerido de TODOS los bolsillos con meta. Si uno falla,
        guarda el error de ese bolsillo y sigue con los demás."""
        if fecha_actual is None:
            fecha_actual = date.today()

        resultados = {}
        for nombre, bolsillo in self.billetera.bolsillos.items():
            if bolsillo.monto_meta is not None:
                try:
                    resultados[nombre] = self.ahorro_de_bolsillo(nombre, fecha_actual)
                except BilleteraError as error:
                    resultados[nombre] = {"error": str(error)}
        return resultados

    # ------------------------------------------------------------------
    # Proyección de gastos e ingresos
    # ------------------------------------------------------------------

    def predecir_gastos_e_ingresos(self, fecha_actual: date = None) -> dict:
        if fecha_actual is None:
            fecha_actual = date.today()
        mes_actual = fecha_actual.month
        anio_actual = fecha_actual.year

        gastos_por_mes = {}
        ingresos_por_mes = {}
        meses_registrados = set()

        for transaccion in self.billetera.historial:
            t_mes = transaccion.fecha.month
            t_anio = transaccion.fecha.year

            # El mes en curso no está completo: no se usa para promediar.
            if t_anio == anio_actual and t_mes == mes_actual:
                continue

            clave_mes = (t_anio, t_mes)

            # El mes solo se registra si hubo gasto o ingreso (no movimientos neutros).
            if transaccion.tipo in constantes.TIPOS_GASTO:
                meses_registrados.add(clave_mes)
                gastos_por_mes[clave_mes] = gastos_por_mes.get(clave_mes, 0.0) + transaccion.monto
            elif transaccion.tipo in constantes.TIPOS_INGRESO:
                meses_registrados.add(clave_mes)
                ingresos_por_mes[clave_mes] = ingresos_por_mes.get(clave_mes, 0.0) + transaccion.monto

        if len(meses_registrados) < 1:
            return {"suficiente_historial": False}

        lista_gastos = [gastos_por_mes.get(mes, 0.0) for mes in meses_registrados]
        lista_ingresos = [ingresos_por_mes.get(mes, 0.0) for mes in meses_registrados]

        gasto_proyectado = statistics.mean(lista_gastos)
        ingreso_proyectado = statistics.mean(lista_ingresos)

        saldo_proyectado = self.billetera.disponible + ingreso_proyectado - gasto_proyectado
        alerta_riesgo = gasto_proyectado > ingreso_proyectado

        return {
            "suficiente_historial": True,
            "gasto_estimado": float(gasto_proyectado),
            "ingreso_estimado": float(ingreso_proyectado),
            "saldo_proyectado": float(saldo_proyectado),
            "alerta_riesgo": alerta_riesgo,
        }

    # ------------------------------------------------------------------
    # Estadísticas
    # ------------------------------------------------------------------

    def estadisticas(self, inicio: date = None, fin: date = None) -> dict:
        total_gastado = 0.0
        total_ingresado = 0.0
        numero_transacciones = 0

        for transaccion in self.billetera.historial:
            fecha = self._a_fecha(transaccion.fecha)
            if inicio is not None and fecha < inicio:
                continue
            if fin is not None and fecha > fin:
                continue

            numero_transacciones += 1
            if transaccion.tipo in constantes.TIPOS_GASTO:
                total_gastado += transaccion.monto
            elif transaccion.tipo in constantes.TIPOS_INGRESO:
                total_ingresado += transaccion.monto

        if numero_transacciones == 0:
            return {"hay_datos": False}

        return {
            "hay_datos": True,
            "total_gastado": total_gastado,
            "total_ingresado": total_ingresado,
            "numero_transacciones": numero_transacciones,
        }
