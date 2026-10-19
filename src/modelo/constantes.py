
# Rentabilidades
RENTABILIDAD_BOLSILLO: float = 0.07
RENTABILIDAD_CDT: float = 0.095

# 4x1000
IMPUESTO_4X1000: float = 0.004
VALOR_UVT = 49799
TOPE_MENSUAL = 65  
TIPOS_COBRO_4X1000 = ["retiro", "envio_saliente"]

# CDT
MONTO_MINIMO_CDT = 500000

# Divisas
MONEDAS = ["COP", "USD", "EUR"]
TASAS_DE_CAMBIO = {
    ("COP", "USD"): 0.00025,
    ("USD", "COP"): 3200,
    ("COP", "EUR"): 0.00023,
}

# Tipos de transacciones
TIPOS_GASTO = ["retiro", "envio_saliente", "recarga_civica", "cambio_divisa"]
TIPOS_INGRESO = ["deposito", "envio_entrante"]
