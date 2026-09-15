"""
Test 3: validaciones, casos de error y bordes del sistema
Cubre: Billetera (depositar_dinero inválido, retirar_dinero insuficiente,
crear_bolsillo validaciones, mover_entre_bolsillos errores, crear_cdt errores,
cambiar_divisas errores, enviar errores, recargarCivica inválido,
calcular_4x1000 cuando SÍ se cobra impuesto)
Bolsillo (retirar insuficiente, depositar inválido, meta ya alcanzada -> ahorro 0.0)
Tarjeta (unicidad de números entre muchas tarjetas)
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


linea("1. Depositar dinero con monto inválido")
billetera = m.Billetera(disponible=1_000_000)
usuario = m.Usuario("Marta", "3001", 4_000_000, billetera)

try:
    billetera.depositar_dinero(-500)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera.depositar_dinero(0)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("2. Retirar dinero con fondos insuficientes")
try:
    billetera.retirar_dinero(50_000_000)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("3. Bolsillo: depositar/retirar con montos inválidos")
billetera.crear_bolsillo("prueba")
bolsillo_prueba = billetera.bolsillos["prueba"]

try:
    bolsillo_prueba.depositar(-100)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    bolsillo_prueba.retirar(10_000)  # el bolsillo está vacío
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("4. crear_bolsillo: validaciones de argumentos")
# monto_meta sin fecha_meta
try:
    billetera.crear_bolsillo("incompleto", monto_meta=500_000)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

# nombre duplicado
try:
    billetera.crear_bolsillo("prueba")
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

# fecha meta en el pasado
try:
    billetera.crear_bolsillo(
        "viaje_pasado", monto_meta=1_000_000, fecha_meta=date.today() - timedelta(days=1)
    )
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("5. mover_entre_bolsillos: casos de error")
try:
    billetera.mover_entre_bolsillos(bolsillo_destino="no_existe", monto=10_000)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera.mover_entre_bolsillos(
        bolsillo_destino="prueba", monto=10_000, bolsillo_origen="tampoco_existe"
    )
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera.mover_entre_bolsillos(bolsillo_destino="prueba", monto=999_999_999)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

# intentar usar mover_entre_bolsillos con una divisa (debe redirigir a cambiar_divisas)
try:
    billetera.mover_entre_bolsillos(bolsillo_destino="USD", monto=10_000)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("6. crear_cdt: validaciones")
try:
    billetera.crear_cdt(monto=1_000, plazo_meses=6)  # menor al mínimo
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera.crear_cdt(monto=1_000_000, plazo_meses=0)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera.crear_cdt(monto=1_000_000, plazo_meses=6, origen="prueba")  # bolsillo sin fondos
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("7. cambiar_divisas: validaciones")
try:
    billetera.cambiar_divisas(monto=10_000, tipo_divisa=("COP", "JPY"))  # no soportada
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera.cambiar_divisas(monto=999_999_999, tipo_divisa=("COP", "USD"))
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("8. enviar: validaciones")
billetera_destino = m.Billetera(disponible=0.0)
usuario_destino = m.Usuario("Pedro", "3002", 2_000_000, billetera_destino)

try:
    billetera.enviar(monto=-100, destinatario=usuario_destino)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera.enviar(monto=10_000, destinatario=usuario_destino, origen="no_existe")
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")

try:
    billetera.enviar(monto=999_999_999, destinatario=usuario_destino)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("9. recargarCivica con monto inválido")
billetera.crearTarjetaCivica()
civica = billetera.tarjetas[-1]
try:
    billetera.recargarCivica(-5_000, civica)
    print("❌ No lanzó error, y debía")
except ValueError as error:
    print(f"Error esperado capturado: {error}")


linea("10. calcular_4x1000 cuando SÍ se cobra impuesto (supera el tope mensual exento)")
billetera_rica = m.Billetera(disponible=100_000_000_000)
tope_exento = m.TOPE_MENSUAL * m.VALOR_UVT
print(f"Tope mensual exento: {tope_exento}")

# retiro grande que ya supera el tope exento por sí solo
impuesto = billetera_rica.calcular_4x1000(tope_exento + 1_000_000)
print(f"Impuesto calculado sobre un monto que supera el tope: {impuesto}")
assert impuesto > 0, "Debería cobrar 4x1000 al superar el tope exento"

# ahora that el acumulado ya está en el historial, cualquier monto adicional paga completo
billetera_rica.retirar_dinero(tope_exento + 1_000_000)
impuesto_2 = billetera_rica.calcular_4x1000(100_000)
print(f"Impuesto sobre un retiro adicional una vez superado el tope: {impuesto_2}")
assert impuesto_2 == 100_000 * m.IMPUESTO_4X1000


linea("11. Bolsillo con meta ya alcanzada -> ahorro sugerido debe ser 0.0")
billetera.crear_bolsillo(
    "meta_lista", monto_meta=100_000, fecha_meta=date.today() + timedelta(days=30)
)
billetera.mover_entre_bolsillos(bolsillo_destino="meta_lista", monto=150_000)
sugerido = billetera.bolsillos["meta_lista"].calcular_ahorro_mensual_sugerido()
print(f"Ahorro sugerido con meta ya superada: {sugerido}")
assert sugerido == 0.0


linea("12. Unicidad de números de tarjeta entre varias tarjetas")
numeros_generados = set()
for _ in range(20):
    billetera.crearTarjetaDebito()
for tarjeta in billetera.tarjetas:
    assert tarjeta.numero not in numeros_generados, "Se repitió un número de tarjeta"
    numeros_generados.add(tarjeta.numero)
print(f"Se generaron {len(numeros_generados)} números de tarjeta únicos, sin repetidos")


print("\n✅ test3.py terminó sin errores")