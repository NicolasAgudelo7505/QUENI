"""
Test 2: CDTs, cambio de divisas y proyección financiera
Cubre: Billetera (crear_cdt, cambiar_divisas, predecir_gastos_e_ingresos)
CDT (calcular_valor_proyectado)
Bolsillo (calcular_ahorro_mensual_sugerido con caso de error)
Usuario (calcular_ahorro_mensual con meta no viable)
"""
from datetime import date, timedelta
import modelo as m


def linea(titulo):
    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)


linea("1. Crear billetera con saldo inicial")
billetera = m.Billetera(disponible=5_000_000)
usuario = m.Usuario("Carlos", "2002", 3_000_000, billetera)
print(f"Disponible inicial: {billetera.consultar_disponible()}")

linea("2. CDT (crear_cdt + calcular_valor_proyectado)")
billetera.crear_cdt(monto=1_000_000, plazo_meses=12)
print(f"Disponible tras abrir CDT: {billetera.consultar_disponible()}")
assert billetera.consultar_disponible() == 4_000_000

cdt = billetera.cdts[0]
print(f"CDT: monto={cdt.monto}, tasa={cdt.tasa_interes}, plazo={cdt.plazo_meses} meses")
valor_final = cdt.calcular_valor_proyectado()
print(f"Valor proyectado al vencimiento: {valor_final:.2f}")
assert valor_final > cdt.monto

# CDT financiado desde un bolsillo
billetera.crear_bolsillo("ahorro_cdt")
billetera.mover_entre_bolsillos(bolsillo_destino="ahorro_cdt", monto=800_000)
billetera.crear_cdt(monto=600_000, plazo_meses=6, origen="ahorro_cdt")
print(f"Bolsillo 'ahorro_cdt' tras abrir segundo CDT: {billetera.bolsillos['ahorro_cdt'].saldo}")
print(f"Cantidad de CDTs abiertos: {len(billetera.cdts)}")
assert len(billetera.cdts) == 2

linea("3. Cambio de divisas")
billetera.cambiar_divisas(monto=100_000, tipo_divisa=("COP", "USD"))
print(f"Disponible tras comprar USD: {billetera.consultar_disponible()}")
print(f"Bolsillo USD creado automáticamente: {billetera.bolsillos['USD'].saldo}")
assert "USD" in billetera.bolsillos
assert billetera.bolsillos["USD"].saldo == 100_000 * m.TASAS_DE_CAMBIO[("COP", "USD")]

# Cambio de divisas desde un bolsillo en COP hacia EUR
billetera.crear_bolsillo("viaje")
billetera.mover_entre_bolsillos(bolsillo_destino="viaje", monto=300_000)
billetera.cambiar_divisas(monto=100_000, tipo_divisa=("COP", "EUR"), origen="viaje")
print(f"Bolsillo 'viaje' (COP) tras cambio: {billetera.bolsillos['viaje'].saldo}")
print(f"Bolsillo 'EUR' creado: {billetera.bolsillos['EUR'].saldo}")
assert "EUR" in billetera.bolsillos

linea("4. Bolsillo con meta ya vencida (caso de error controlado)")
bolsillo_vencido = m.Bolsillo(
    nombre="meta_vencida", monto_meta=1_000_000, fecha_meta=date.today() - timedelta(days=5)
)
try:
    bolsillo_vencido.calcular_ahorro_mensual_sugerido()
except ValueError as error:
    print(f"Error esperado capturado: {error}")

linea("5. Meta no viable con el sueldo del usuario")
billetera.crear_bolsillo(
    "casa", monto_meta=500_000_000, fecha_meta=date.today() + timedelta(days=60)
)
resultado = usuario.calcular_ahorro_mensual(billetera.bolsillos["casa"])
print(f"Resultado meta 'casa': {resultado}")
assert resultado["viable"] is False

linea("6. Predicción de gastos e ingresos")
# Sin historial de meses anteriores todavía
prediccion_vacia = billetera.predecir_gastos_e_ingresos()
print(f"Predicción sin historial suficiente: {prediccion_vacia}")
assert prediccion_vacia["suficiente_historial"] is False

# Simulamos historial de los dos meses anteriores modificando la fecha directamente
hoy = date.today()
mes_pasado = date(hoy.year, hoy.month, 1) - timedelta(days=1)
dos_meses_atras = date(mes_pasado.year, mes_pasado.month, 1) - timedelta(days=1)

billetera.depositar_dinero(1_000_000)
billetera.historial[-1].fecha = mes_pasado
billetera.retirar_dinero(200_000)
billetera.historial[-1].fecha = mes_pasado

billetera.depositar_dinero(1_200_000)
billetera.historial[-1].fecha = dos_meses_atras
billetera.retirar_dinero(300_000)
billetera.historial[-1].fecha = dos_meses_atras

prediccion = billetera.predecir_gastos_e_ingresos()
print(f"Predicción con historial: {prediccion}")
assert prediccion["suficiente_historial"] is True

linea("7. Historial completo (Transaccion.mostrar_info)")
for linea_hist in billetera.consultar_historial_transacciones():
    print(" -", linea_hist)

print("\n✅ test_billetera_2.py terminó sin errores")
