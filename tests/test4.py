"""
Test 4 (integral): todas las funcionalidades y todas las excepciones

Recorre los 15 requerimientos funcionales (R1 a R15) con su camino exitoso
y la excepción que le corresponde. Al final verifica automáticamente que se
hayan probado las 15 excepciones personalizadas del proyecto.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from datetime import date, timedelta
import modelo as m


def linea(titulo):
    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)


# Aquí se anota el nombre de cada excepción que se logra provocar.
excepciones_cubiertas = set()


def anotar(error):
    excepciones_cubiertas.add(type(error).__name__)
    print(f"   Error esperado ({type(error).__name__}): {error}")


queni = m.QUENI()


linea("R15. Registrar usuario")
usuario_ana = queni.registrar_usuario("Ana", "1001", 3_000_000, saldo_inicial=3_000_000)
usuario_luis = queni.registrar_usuario("Luis", "1002", 2_500_000)
ana = usuario_ana.billetera
luis = usuario_luis.billetera
print(f"Ana: cuenta {ana.numero_cuenta}, disponible {ana.consultar_disponible()}")
print(f"Luis: cuenta {luis.numero_cuenta}, disponible {luis.consultar_disponible()}")
assert queni.buscar_usuario("1001") is usuario_ana
assert queni.buscar_cuenta(luis.numero_cuenta) is luis
assert ana.numero_cuenta != luis.numero_cuenta

try:
    queni.registrar_usuario("Ana Repetida", "1001", 1_000_000)
    raise AssertionError("Debía lanzar UsuarioDuplicadoError")
except m.UsuarioDuplicadoError as error:
    anotar(error)

try:
    queni.buscar_usuario("9999")
    raise AssertionError("Debía lanzar UsuarioNoExisteError")
except m.UsuarioNoExisteError as error:
    anotar(error)


linea("R2. Guardar dinero (disponible y bolsillo)")
ana.depositar_dinero(500_000)
print(f"Disponible de Ana tras depositar 500.000: {ana.consultar_disponible()}")
assert ana.consultar_disponible() == 3_500_000

try:
    ana.depositar_dinero(-500)
    raise AssertionError("Debía lanzar MontoInvalidoError")
except m.MontoInvalidoError as error:
    anotar(error)


linea("R1. Crear un bolsillo")
ana.crear_bolsillo("vacaciones")
ana.crear_bolsillo("moto", monto_meta=6_000_000, fecha_meta=date.today() + timedelta(days=360))
print(f"Bolsillos de Ana: {list(ana.bolsillos.keys())}")
assert set(ana.bolsillos.keys()) == {"vacaciones", "moto"}
assert ana.bolsillos["vacaciones"].saldo == 0

try:
    ana.crear_bolsillo("vacaciones")
    raise AssertionError("Debía lanzar BolsilloDuplicadoError")
except m.BolsilloDuplicadoError as error:
    anotar(error)

try:
    ana.crear_bolsillo("sin_fecha", monto_meta=500_000)
    raise AssertionError("Debía lanzar MetaInvalidaError")
except m.MetaInvalidaError as error:
    anotar(error)

ana.depositar_dinero(100_000, destino="vacaciones")
print(f"Depósito directo en el bolsillo 'vacaciones': {ana.bolsillos['vacaciones'].saldo}")
assert ana.bolsillos["vacaciones"].saldo == 100_000


linea("R6. Consultar disponible")
print(f"Disponible de Ana: {ana.consultar_disponible()} | Luis: {luis.consultar_disponible()}")
assert ana.consultar_disponible() == 3_500_000
assert luis.consultar_disponible() == 0


linea("R3. Retirar dinero (disponible y bolsillo)")
disponible_antes = ana.consultar_disponible()
ana.retirar_dinero(100_000)
print(f"Retiro de 100.000 del disponible: {disponible_antes} -> {ana.consultar_disponible()}")
assert ana.consultar_disponible() == disponible_antes - 100_000

ana.retirar_dinero(20_000, origen="vacaciones")
print(f"Retiro de 20.000 del bolsillo 'vacaciones': {ana.bolsillos['vacaciones'].saldo}")
assert ana.bolsillos["vacaciones"].saldo == 80_000

try:
    ana.retirar_dinero(50_000_000)
    raise AssertionError("Debía lanzar SaldoInsuficienteError")
except m.SaldoInsuficienteError as error:
    anotar(error)
    assert error.saldo == ana.consultar_disponible()


linea("R5. Mover dinero entre bolsillos")
ana.mover_entre_bolsillos(bolsillo_destino="moto", monto=300_000)
ana.mover_entre_bolsillos(bolsillo_destino="vacaciones", monto=30_000, bolsillo_origen="moto")
print(f"Moto: {ana.bolsillos['moto'].saldo} | Vacaciones: {ana.bolsillos['vacaciones'].saldo}")
assert ana.bolsillos["moto"].saldo == 270_000
assert ana.bolsillos["vacaciones"].saldo == 110_000
assert ana.historial[-1].tipo == "movimiento_bolsillos"

try:
    ana.mover_entre_bolsillos(bolsillo_destino="no_existe", monto=10_000)
    raise AssertionError("Debía lanzar BolsilloNoExisteError")
except m.BolsilloNoExisteError as error:
    anotar(error)

try:
    ana.mover_entre_bolsillos(bolsillo_destino="USD", monto=10_000)
    raise AssertionError("Debía lanzar OperacionNoPermitidaError")
except m.OperacionNoPermitidaError as error:
    anotar(error)


linea("R7. Crear tarjeta (débito y cívica) y asignarla a una cuenta")
queni.asignar_tarjeta_debito(ana.numero_cuenta)
queni.asignar_tarjeta_civica(ana.numero_cuenta)
debito_ana = ana.tarjetas["Debito"]
civica_ana = ana.tarjetas["Civica"]
print(f"Débito #{debito_ana.numero} | Cívica #{civica_ana.numero} | Tarjetas de Ana: {len(ana.tarjetas)}")
assert len(ana.tarjetas) == 2
assert debito_ana.numero != civica_ana.numero
assert isinstance(civica_ana, m.Civica) and civica_ana.saldo == 0

# QUENI lleva el registro de los números emitidos, por tipo de tarjeta
assert debito_ana.numero in queni.tarjetas["Debito"]
assert civica_ana.numero in queni.tarjetas["Civica"]

debitos_emitidos = len(queni.tarjetas["Debito"])
civicas_emitidas = len(queni.tarjetas["Civica"])

try:
    queni.asignar_tarjeta_debito(ana.numero_cuenta)
    raise AssertionError("Debía lanzar TarjetaDuplicadaError")
except m.TarjetaDuplicadaError as error:
    anotar(error)
    assert error.tipo == "Debito"

try:
    queni.asignar_tarjeta_civica(ana.numero_cuenta)
    raise AssertionError("Debía lanzar TarjetaDuplicadaError")
except m.TarjetaDuplicadaError as error:
    anotar(error)
    assert error.tipo == "Civica"

# Una asignación rechazada no debe dejar números emitidos "huérfanos"
assert len(queni.tarjetas["Debito"]) == debitos_emitidos, "Se registró un número de débito aunque la asignación falló"
assert len(queni.tarjetas["Civica"]) == civicas_emitidas, "Se registró un número de cívica aunque la asignación falló"
assert ana.tarjetas["Debito"] is debito_ana and ana.tarjetas["Civica"] is civica_ana, "La tarjeta original no debe reemplazarse"

try:
    queni.asignar_tarjeta_debito(1234567890)    # la cuenta no existe
    raise AssertionError("Debía lanzar CuentaNoExisteError")
except m.CuentaNoExisteError as error:
    anotar(error)
assert len(queni.tarjetas["Debito"]) == debitos_emitidos, "No debe emitirse una tarjeta para una cuenta inexistente"

# Unicidad: 25 usuarios con ambas tarjetas, todos los números distintos
for i in range(25):
    nuevo = queni.registrar_usuario(f"Usuario{i}", f"doc{i}", 1_000_000)
    queni.asignar_tarjeta_debito(nuevo.billetera.numero_cuenta)
    queni.asignar_tarjeta_civica(nuevo.billetera.numero_cuenta)
assert len(queni.tarjetas["Debito"]) == len(set(queni.tarjetas["Debito"])) == debitos_emitidos + 25
assert len(queni.tarjetas["Civica"]) == len(set(queni.tarjetas["Civica"])) == civicas_emitidas + 25
print(f"Con 25 usuarios más: {len(queni.tarjetas['Debito'])} débitos y {len(queni.tarjetas['Civica'])} cívicas, todos los números distintos")


linea("R12. Recargar tarjeta Cívica")
disponible_antes = ana.consultar_disponible()
ana.recargar_civica(15_000, civica_ana)
ana.recargar_civica(5_000, civica_ana, origen="vacaciones")
print(f"Saldo de la cívica: {civica_ana.saldo} | disponible: {disponible_antes} -> {ana.consultar_disponible()}")
assert civica_ana.saldo == 20_000
assert ana.consultar_disponible() == disponible_antes - 15_000
assert ana.bolsillos["vacaciones"].saldo == 105_000
assert ana.historial[-1].tipo == "recarga_civica"

queni.asignar_tarjeta_civica(luis.numero_cuenta)
civica_luis = luis.tarjetas["Civica"]
try:
    ana.recargar_civica(10_000, civica_luis)   # cívica de otra billetera
    raise AssertionError("Debía lanzar TarjetaNoExisteError")
except m.TarjetaNoExisteError as error:
    anotar(error)
assert civica_luis.saldo == 0, "No debe recargarse una tarjeta ajena"

sin_tarjetas = queni.registrar_usuario("Sin Tarjetas", "1010", 1_000_000, saldo_inicial=100_000)
try:
    sin_tarjetas.billetera.recargar_civica(10_000, civica_luis)   # la billetera no tiene cívica
    raise AssertionError("Debía lanzar TarjetaNoExisteError")
except m.TarjetaNoExisteError as error:
    anotar(error)
assert sin_tarjetas.billetera.consultar_disponible() == 100_000, "No debe debitarse si la tarjeta no existe"


linea("R8. Crear un CDT")
disponible_antes = ana.consultar_disponible()
ana.crear_cdt(monto=600_000, plazo_meses=12)
cdt = ana.cdts[0]
print(f"CDT 1: monto={cdt.monto}, tasa={cdt.tasa_interes}, plazo={cdt.plazo_meses}, vence={cdt.fecha_vencimiento}")
print(f"Valor proyectado: {cdt.calcular_valor_proyectado():.2f}")
print(f"Disponible: {disponible_antes} -> {ana.consultar_disponible()}")
assert ana.consultar_disponible() == disponible_antes - 600_000
assert cdt.calcular_valor_proyectado() > cdt.monto

# CDT financiado desde un bolsillo
ana.crear_bolsillo("ahorro_cdt")
ana.mover_entre_bolsillos(bolsillo_destino="ahorro_cdt", monto=500_000)
ana.crear_cdt(monto=500_000, plazo_meses=6, origen="ahorro_cdt")
print(f"CDT 2 desde el bolsillo 'ahorro_cdt' (queda en {ana.bolsillos['ahorro_cdt'].saldo}); CDTs abiertos: {len(ana.cdts)}")
assert len(ana.cdts) == 2
assert ana.bolsillos["ahorro_cdt"].saldo == 0

try:
    ana.crear_cdt(monto=1_000, plazo_meses=6)
    raise AssertionError("Debía lanzar CDTInvalidoError")
except m.CDTInvalidoError as error:
    anotar(error)


linea("R10. Realizar cambio de divisas")
disponible_antes = ana.consultar_disponible()
ana.cambiar_divisas(monto=100_000, tipo_divisa=("COP", "USD"))
print(f"Bolsillo USD: {ana.bolsillos['USD'].saldo} | disponible: {disponible_antes} -> {ana.consultar_disponible()}")
assert ana.bolsillos["USD"].saldo == 100_000 * m.TASAS_DE_CAMBIO[("COP", "USD")]
assert ana.historial[-1].tasa_aplicada == m.TASAS_DE_CAMBIO[("COP", "USD")]

ana.cambiar_divisas(monto=50_000, tipo_divisa=("COP", "EUR"), origen="vacaciones")
print(f"Bolsillo EUR: {ana.bolsillos['EUR'].saldo} | vacaciones: {ana.bolsillos['vacaciones'].saldo}")
assert ana.bolsillos["vacaciones"].saldo == 55_000

try:
    ana.cambiar_divisas(monto=10_000, tipo_divisa=("COP", "JPY"))
    raise AssertionError("Debía lanzar DivisaNoSoportadaError")
except m.DivisaNoSoportadaError as error:
    anotar(error)


linea("R4. Enviar dinero por número de cuenta + 4x1000")
disponible_ana = ana.consultar_disponible()
impuesto = queni.enviar("1001", luis.numero_cuenta, 50_000)
print(f"Envío de 50.000: impuesto {impuesto} | Ana {disponible_ana} -> {ana.consultar_disponible()} "
      f"| Luis {luis.consultar_disponible()}")
assert luis.consultar_disponible() == 50_000
assert ana.consultar_disponible() == disponible_ana - 50_000 - impuesto
assert ana.historial[-1].tipo == "envio_saliente"
assert luis.historial[-1].tipo == "envio_entrante"

queni.enviar("1001", luis.numero_cuenta, 10_000, bolsillo_origen="vacaciones")
assert luis.consultar_disponible() == 60_000
assert ana.bolsillos["vacaciones"].saldo == 45_000

try:
    queni.enviar("1001", 1234567890, 10_000)
    raise AssertionError("Debía lanzar CuentaNoExisteError")
except m.CuentaNoExisteError as error:
    anotar(error)

try:
    queni.enviar("1001", ana.numero_cuenta, 10_000)
    raise AssertionError("Debía lanzar OperacionNoPermitidaError")
except m.OperacionNoPermitidaError as error:
    anotar(error)

print("\n   -> 4x1000 superando el tope exento:")
rico = queni.registrar_usuario("Rico", "9001", 9_000_000, saldo_inicial=100_000_000_000)
tope_exento = m.TOPE_MENSUAL * m.VALOR_UVT
print(f"   Tope mensual exento: {tope_exento}")
assert rico.billetera.calcular_4x1000(1_000_000) == 0
rico.billetera.retirar_dinero(tope_exento + 1_000_000)
impuesto_rico = rico.billetera.historial[-1].impuesto_4x1000
print(f"   Retiro que cruza el tope: impuesto cobrado = {impuesto_rico}")
assert abs(impuesto_rico - 1_000_000 * m.IMPUESTO_4X1000) < 1e-6
siguiente = rico.billetera.calcular_4x1000(100_000)
assert abs(siguiente - 100_000 * m.IMPUESTO_4X1000) < 1e-6
print(f"   Impuesto sobre 100.000 una vez superado el tope: {siguiente}")


linea("R9. Consultar historial de transacciones")
for linea_hist in ana.consultar_historial_transacciones():
    print(" -", linea_hist)
tipos_ana = {t.tipo for t in ana.historial}
print(f"\nTipos registrados en el historial de Ana: {sorted(tipos_ana)}")
assert {"deposito", "retiro", "movimiento_bolsillos", "recarga_civica",
        "cambio_divisa", "envio_saliente"} <= tipos_ana
assert all(t.saldo_resultante is not None for t in ana.historial)


linea("R11. Calcular ahorro mensual sugerido según metas")
analizador_ana = queni.analizador("1001")
print(f"Ahorro de 'moto': {analizador_ana.ahorro_de_bolsillo('moto')}")
print(f"Ahorro de todos los bolsillos con meta: {analizador_ana.ahorro_mensual_sugerido()}")

ana.crear_bolsillo("casa", monto_meta=500_000_000, fecha_meta=date.today() + timedelta(days=60))
resultado_casa = analizador_ana.ahorro_de_bolsillo("casa")
print(f"Meta 'casa' (no viable con el sueldo): {resultado_casa}")
assert resultado_casa["viable"] is False

try:
    analizador_ana.ahorro_de_bolsillo("vacaciones")   # no tiene meta
    raise AssertionError("Debía lanzar MetaNoDefinidaError")
except m.MetaNoDefinidaError as error:
    anotar(error)

ana.bolsillos["moto"].fecha_meta = date.today() - timedelta(days=5)   # se vence la meta
try:
    analizador_ana.ahorro_de_bolsillo("moto")
    raise AssertionError("Debía lanzar MetaVencidaError")
except m.MetaVencidaError as error:
    anotar(error)
print(f"Con la meta vencida, el reporte general no se cae: {analizador_ana.ahorro_mensual_sugerido()['moto']}")


linea("R13. Predecir gastos e ingresos futuros")
analizador_luis = queni.analizador("1002")
assert analizador_luis.predecir_gastos_e_ingresos() == {"suficiente_historial": False}
print("Sin historial de meses anteriores: no hay datos suficientes (correcto)")

hoy = date.today()
mes_pasado = date(hoy.year, hoy.month, 1) - timedelta(days=1)
dos_meses_atras = date(mes_pasado.year, mes_pasado.month, 1) - timedelta(days=1)

luis.depositar_dinero(1_000_000)
luis.historial[-1].fecha = mes_pasado
luis.retirar_dinero(200_000)
luis.historial[-1].fecha = mes_pasado
luis.depositar_dinero(1_200_000)
luis.historial[-1].fecha = dos_meses_atras
luis.retirar_dinero(300_000)
luis.historial[-1].fecha = dos_meses_atras

prediccion = analizador_luis.predecir_gastos_e_ingresos()
print(f"Predicción de Luis: {prediccion}")
assert prediccion["suficiente_historial"] is True
assert prediccion["gasto_estimado"] == 250_000
assert prediccion["ingreso_estimado"] == 1_100_000
assert prediccion["alerta_riesgo"] is False

luis.retirar_dinero(10_000)
luis.historial[-1].fecha = date(hoy.year - 1, 6, 10)    # un tercer mes antiguo, con solo gasto
prediccion_3_meses = analizador_luis.predecir_gastos_e_ingresos()
print(f"Con un tercer mes de solo gasto: {prediccion_3_meses}")
assert prediccion_3_meses["gasto_estimado"] == (200_000 + 300_000 + 10_000) / 3
assert abs(prediccion_3_meses["ingreso_estimado"] - (1_000_000 + 1_200_000 + 0) / 3) < 1e-6


linea("R14. Consultar estadísticas del usuario")
estadisticas = analizador_ana.estadisticas()
print(f"Estadísticas de Ana: {estadisticas}")
assert estadisticas["hay_datos"] is True
assert estadisticas["numero_transacciones"] == len(ana.historial)

desde_hoy = analizador_ana.estadisticas(inicio=hoy)
assert desde_hoy["numero_transacciones"] == len(ana.historial)
print(f"Estadísticas de Ana desde hoy: {desde_hoy}")

futuro = analizador_ana.estadisticas(inicio=hoy + timedelta(days=1))
assert futuro == {"hay_datos": False}
print(f"Estadísticas en un periodo sin transacciones: {futuro}")


linea("Verificación final: ¿se probaron todas las excepciones?")
esperadas = {
    "MontoInvalidoError", "SaldoInsuficienteError", "BolsilloNoExisteError",
    "BolsilloDuplicadoError", "MetaInvalidaError", "MetaNoDefinidaError",
    "MetaVencidaError", "CDTInvalidoError", "DivisaNoSoportadaError",
    "OperacionNoPermitidaError", "TarjetaNoExisteError", "TarjetaDuplicadaError",
    "UsuarioDuplicadoError", "UsuarioNoExisteError", "CuentaNoExisteError",
}
print(f"Excepciones provocadas: {len(excepciones_cubiertas)} de {len(esperadas)}")
faltan = esperadas - excepciones_cubiertas
assert not faltan, f"Faltan por probar: {faltan}"
print("Se probaron las 15 excepciones personalizadas")

print("\n✅ test4.py terminó sin errores")