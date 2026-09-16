"""
Test 1: flujo básico de una billetera
Cubre: Billetera (init, depositar_dinero, retirar_dinero, consultar_disponible,
consultar_historial_transacciones, crearTarjetaDebito, crearTarjetaCivica,
recargarCivica, crear_bolsillo, mover_entre_bolsillos, enviar, calcular_4x1000)
Bolsillo (depositar, retirar, calcular_rendimiento_mensual)
Tarjeta/TarjetaDebito/Civica (crearTarjeta -> se llama en el __init__, recargar)
Transaccion (mostrar_info)
Usuario (creación)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from datetime import date
import modelo as m


def linea(titulo):
    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)


linea("1. Crear billeteras y usuarios")
billetera_ana = m.Billetera(disponible=0.0)
usuario_ana = m.Usuario("Ana", "1001", 3_000_000, billetera_ana)

billetera_luis = m.Billetera(disponible=0.0)
usuario_luis = m.Usuario("Luis", "1002", 2_500_000, billetera_luis)

print(f"Número de cuenta de Ana:  {billetera_ana.numeroCuenta}")
print(f"Número de cuenta de Luis: {billetera_luis.numeroCuenta}")
assert billetera_ana.numeroCuenta != 0, "El número de cuenta no se generó bien"
assert billetera_ana.numeroCuenta != billetera_luis.numeroCuenta

linea("2. Depositar y retirar dinero")
billetera_ana.depositar_dinero(1_000_000)
print(f"Disponible Ana tras depósito: {billetera_ana.consultar_disponible()}")
assert billetera_ana.consultar_disponible() == 1_000_000

billetera_ana.retirar_dinero(100_000)
print(f"Disponible Ana tras retiro: {billetera_ana.consultar_disponible()}")
# El retiro descuenta 100.000 + 4x1000 (que en este caso es 0 porque no supera el tope exento)
assert billetera_ana.consultar_disponible() == 900_000

linea("3. Tarjetas (débito y cívica) + recarga")
billetera_ana.crearTarjetaDebito()
billetera_ana.crearTarjetaCivica()
print(f"Tarjetas de Ana: {len(billetera_ana.tarjetas)}")
assert len(billetera_ana.tarjetas) == 2

civica_ana = billetera_ana.tarjetas[1]
print(f"Número de la cívica: {civica_ana.numero} | saldo inicial: {civica_ana.saldo}")
billetera_ana.recargarCivica(15_000, civica_ana)
print(f"Saldo cívica tras recarga: {civica_ana.saldo}")
assert civica_ana.saldo == 15_000

linea("4. Bolsillos (crear, depositar, retirar, mover, rendimiento)")
billetera_ana.crear_bolsillo("vacaciones")
billetera_ana.mover_entre_bolsillos(bolsillo_destino="vacaciones", monto=200_000)
print(f"Saldo bolsillo 'vacaciones': {billetera_ana.bolsillos['vacaciones'].saldo}")
assert billetera_ana.bolsillos["vacaciones"].saldo == 200_000
print(f"Disponible restante: {billetera_ana.consultar_disponible()}")

rendimiento = billetera_ana.bolsillos["vacaciones"].calcular_rendimiento_mensual()
print(f"Rendimiento mensual estimado del bolsillo: {rendimiento:.2f}")

billetera_ana.crear_bolsillo("emergencias")
billetera_ana.mover_entre_bolsillos(
    bolsillo_destino="emergencias", monto=50_000, bolsillo_origen="vacaciones"
)
print(f"Vacaciones: {billetera_ana.bolsillos['vacaciones'].saldo} | "
      f"Emergencias: {billetera_ana.bolsillos['emergencias'].saldo}")
assert billetera_ana.bolsillos["vacaciones"].saldo == 150_000
assert billetera_ana.bolsillos["emergencias"].saldo == 50_000

# métodos directos de Bolsillo (depositar / retirar)
billetera_ana.bolsillos["emergencias"].depositar(10_000)
billetera_ana.bolsillos["emergencias"].retirar(5_000)
print(f"Emergencias tras depositar/retirar directo: {billetera_ana.bolsillos['emergencias'].saldo}")
assert billetera_ana.bolsillos["emergencias"].saldo == 55_000

linea("5. Envío entre usuarios + impuesto 4x1000")
impuesto_estimado = billetera_ana.calcular_4x1000(50_000)
print(f"Impuesto 4x1000 estimado sobre 50.000: {impuesto_estimado}")

disponible_ana_antes = billetera_ana.consultar_disponible()
disponible_luis_antes = billetera_luis.consultar_disponible()

billetera_ana.enviar(monto=50_000, destinatario=usuario_luis)

print(f"Disponible Ana antes/después: {disponible_ana_antes} -> {billetera_ana.consultar_disponible()}")
print(f"Disponible Luis antes/después: {disponible_luis_antes} -> {billetera_luis.consultar_disponible()}")
assert billetera_luis.consultar_disponible() == disponible_luis_antes + 50_000

# Envío también desde un bolsillo
billetera_ana.enviar(monto=20_000, destinatario=usuario_luis, origen="vacaciones")
print(f"Vacaciones tras envío: {billetera_ana.bolsillos['vacaciones'].saldo}")

linea("6. Historial de transacciones (Transaccion.mostrar_info)")
for linea_hist in billetera_ana.consultar_historial_transacciones():
    print(" -", linea_hist)

linea("7. Ahorro mensual sugerido (bolsillo con meta) + Usuario.calcular_ahorro_mensual")
billetera_ana.crear_bolsillo(
    "moto", monto_meta=6_000_000, fecha_meta=date(date.today().year + 1, 1, 1)
)
resultado_bolsillo = usuario_ana.calcular_ahorro_mensual(billetera_ana.bolsillos["moto"])
print(f"Ahorro sugerido para 'moto': {resultado_bolsillo}")

resultado_todos = billetera_ana.calcular_ahorro_mensual_sugerido(usuario_ana)
print(f"Ahorro sugerido para todos los bolsillos con meta: {resultado_todos}")

linea("8. estadisticas")
print('Gastos de Ana')
print(billetera_ana.mostrar_estadisticas())

print('Gastos de Luis')
print(billetera_luis.mostrar_estadisticas())

print("\n✅ test_billetera_1.py terminó sin errores")
