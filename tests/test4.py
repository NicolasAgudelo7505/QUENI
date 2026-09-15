"""
Test Integral: Billetera Digital Completa
Cubre: Todos los flujos exitosos (Test 1 y 2) y validaciones de errores (Test 3)
para Billetera, Bolsillo, Tarjeta, CDT, Transaccion y Usuario.
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


linea("1. Crear billeteras, usuarios y validación de cuentas")
billetera_ana = m.Billetera(disponible=0.0)
usuario_ana = m.Usuario("Ana", "1001", 3_000_000, billetera_ana)

billetera_luis = m.Billetera(disponible=0.0)
usuario_luis = m.Usuario("Luis", "1002", 2_500_000, billetera_luis)

print(f"Número de cuenta de Ana:  {billetera_ana.numeroCuenta}")
print(f"Número de cuenta de Luis: {billetera_luis.numeroCuenta}")
assert billetera_ana.numeroCuenta != 0, "El número de cuenta no se generó bien"
assert billetera_ana.numeroCuenta != billetera_luis.numeroCuenta


linea("2. Depositar y retirar dinero (Éxitos y Errores)")
billetera_ana.depositar_dinero(1_000_000)
print(f"Disponible Ana tras depósito: {billetera_ana.consultar_disponible()}")
assert billetera_ana.consultar_disponible() == 1_000_000

billetera_ana.retirar_dinero(100_000)
print(f"Disponible Ana tras retiro: {billetera_ana.consultar_disponible()}")
assert billetera_ana.consultar_disponible() == 900_000

print("\n-> Probando errores de depósito y retiro:")
try:
    billetera_ana.depositar_dinero(-500)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera_ana.depositar_dinero(0)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera_ana.retirar_dinero(50_000_000)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("3. Tarjetas (Débito y Cívica), unicidad y recargas")
# Unicidad de números
numeros_generados = set()
for _ in range(20):
    billetera_ana.crearTarjetaDebito()
for tarjeta in billetera_ana.tarjetas:
    assert tarjeta.numero not in numeros_generados, "Se repitió un número de tarjeta"
    numeros_generados.add(tarjeta.numero)
print(f"Se generaron {len(numeros_generados)} números de tarjeta de débito únicos")

billetera_ana.crearTarjetaCivica()
civica_ana = billetera_ana.tarjetas[-1]

print(f"Número de la cívica: {civica_ana.numero} | saldo inicial: {civica_ana.saldo}")
billetera_ana.recargarCivica(15_000, civica_ana)
print(f"Saldo cívica tras recarga: {civica_ana.saldo}")
assert civica_ana.saldo == 15_000

print("\n-> Probando errores de recarga Cívica:")
try:
    billetera_ana.recargarCivica(-5_000, civica_ana)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("4. Bolsillos (Flujos exitosos y Errores)")
billetera_ana.crear_bolsillo("vacaciones")
billetera_ana.mover_entre_bolsillos(bolsillo_destino="vacaciones", monto=200_000)
print(f"Saldo bolsillo 'vacaciones': {billetera_ana.bolsillos['vacaciones'].saldo}")
assert billetera_ana.bolsillos["vacaciones"].saldo == 200_000

billetera_ana.crear_bolsillo("emergencias")
billetera_ana.mover_entre_bolsillos(
    bolsillo_destino="emergencias", monto=50_000, bolsillo_origen="vacaciones"
)
print(f"Vacaciones: {billetera_ana.bolsillos['vacaciones'].saldo} | Emergencias: {billetera_ana.bolsillos['emergencias'].saldo}")

print("\n-> Probando errores al crear bolsillos:")
try:
    billetera_ana.crear_bolsillo("incompleto", monto_meta=500_000)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (meta incompleta): {error}")

try:
    billetera_ana.crear_bolsillo("vacaciones")
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (duplicado): {error}")

try:
    billetera_ana.crear_bolsillo("viaje_pasado", monto_meta=1_000_000, fecha_meta=date.today() - timedelta(days=1))
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (fecha pasada): {error}")

print("\n-> Probando errores al mover entre bolsillos:")
try:
    billetera_ana.mover_entre_bolsillos(bolsillo_destino="no_existe", monto=10_000)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (no existe): {error}")

try:
    billetera_ana.mover_entre_bolsillos(bolsillo_destino="emergencias", monto=999_999_999)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (sin fondos): {error}")

try:
    billetera_ana.mover_entre_bolsillos(bolsillo_destino="USD", monto=10_000)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (movimiento a divisa): {error}")


linea("5. CDTs y Cambio de Divisas")

try:
    billetera_ana.crear_cdt(monto=300_000, plazo_meses=12)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (CDT menor al mínimo): {error}")

billetera_ana.depositar_dinero(1_000_000) 
billetera_ana.crear_cdt(monto=600_000, plazo_meses=12)
cdt = billetera_ana.cdts[0]
valor_final = cdt.calcular_valor_proyectado()
print(f"CDT válido creado: monto={cdt.monto}, meses={cdt.plazo_meses}. Valor proyectado: {valor_final:.2f}")
    
# 3. Cambio de divisas
billetera_ana.cambiar_divisas(monto=50_000, tipo_divisa=("COP", "USD"))
print(f"Bolsillo USD creado automáticamente: {billetera_ana.bolsillos['USD'].saldo}")
assert "USD" in billetera_ana.bolsillos

print("\n-> Probando errores adicionales en CDTs y Divisas:")
try:
    billetera_ana.crear_cdt(monto=1_000_000, plazo_meses=0)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (CDT plazo cero): {error}")

try:
    billetera_ana.cambiar_divisas(monto=10_000, tipo_divisa=("COP", "JPY"))
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (Divisa no soportada): {error}")

linea("6. Envío entre usuarios + Impuesto 4x1000")
disponible_luis_antes = billetera_luis.consultar_disponible()
billetera_ana.enviar(monto=50_000, destinatario=usuario_luis)
print(f"Disponible Luis antes/después: {disponible_luis_antes} -> {billetera_luis.consultar_disponible()}")
assert billetera_luis.consultar_disponible() == disponible_luis_antes + 50_000

print("\n-> Probando errores de envío:")
try:
    billetera_ana.enviar(monto=-100, destinatario=usuario_luis)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera_ana.enviar(monto=999_999_999, destinatario=usuario_luis)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

print("\n-> Probando cálculo 4x1000 superando tope exento:")
billetera_rica = m.Billetera(disponible=100_000_000_000)
tope_exento = m.TOPE_MENSUAL * m.VALOR_UVT
impuesto = billetera_rica.calcular_4x1000(tope_exento + 1_000_000)
print(f"Impuesto calculado sobre un monto que supera el tope: {impuesto}")
assert impuesto > 0, "Debería cobrar 4x1000 al superar el tope exento"

billetera_rica.retirar_dinero(tope_exento + 1_000_000)
impuesto_2 = billetera_rica.calcular_4x1000(100_000)
print(f"Impuesto sobre un retiro adicional una vez superado el tope: {impuesto_2}")
assert impuesto_2 == 100_000 * m.IMPUESTO_4X1000


linea("7. Ahorro Mensual Sugerido (Metas de bolsillos)")
# Meta normal
billetera_ana.crear_bolsillo("moto", monto_meta=6_000_000, fecha_meta=date(date.today().year + 1, 1, 1))
resultado_bolsillo = usuario_ana.calcular_ahorro_mensual(billetera_ana.bolsillos["moto"])
print(f"Ahorro sugerido para 'moto': {resultado_bolsillo}")

# Meta ya alcanzada
billetera_ana.crear_bolsillo("meta_lista", monto_meta=100_000, fecha_meta=date.today() + timedelta(days=30))
billetera_ana.mover_entre_bolsillos(bolsillo_destino="meta_lista", monto=150_000)
sugerido = billetera_ana.bolsillos["meta_lista"].calcular_ahorro_mensual_sugerido()
print(f"Ahorro sugerido con meta ya superada: {sugerido}")
assert sugerido == 0.0

# Meta vencida (Error controlado)
bolsillo_vencido = m.Bolsillo("meta_vencida", 1_000_000, date.today() - timedelta(days=5))
try:
    bolsillo_vencido.calcular_ahorro_mensual_sugerido()
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado (meta vencida): {error}")

# Meta no viable
billetera_ana.crear_bolsillo("casa", monto_meta=500_000_000, fecha_meta=date.today() + timedelta(days=60))
resultado_casa = usuario_ana.calcular_ahorro_mensual(billetera_ana.bolsillos["casa"])
print(f"Resultado meta 'casa' con ingresos limitados: {resultado_casa}")
assert resultado_casa["viable"] is False


linea("8. Predicción de gastos e ingresos")
prediccion_vacia = billetera_luis.predecir_gastos_e_ingresos()
print(f"Predicción sin historial suficiente: {prediccion_vacia}")
assert prediccion_vacia["suficiente_historial"] is False

# Simulamos historial para Ana
hoy = date.today()
mes_pasado = date(hoy.year, hoy.month, 1) - timedelta(days=1)
billetera_ana.depositar_dinero(1_000_000)
billetera_ana.historial[-1].fecha = mes_pasado

prediccion = billetera_ana.predecir_gastos_e_ingresos()
print(f"Predicción con historial modificado: {prediccion}")
assert prediccion["suficiente_historial"] is True


linea("9. Historial completo de transacciones")
print("Mostrando las últimas 5 transacciones de Ana:")
for linea_hist in billetera_ana.consultar_historial_transacciones()[-5:]:
    print(" -", linea_hist)

print("\n✅ test_integral.py terminó sin errores")