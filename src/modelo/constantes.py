# Rentabilidades
RENTABILIDAD_BOLSILLO: float = 0.07  # 7 % E.A. (estilo Nu Cajitas, capitalización diaria)

# 4x1000
IMPUESTO_4X1000: float = 0.004
VALOR_UVT = 49799
TOPE_MENSUAL = 65
TIPOS_COBRO_4X1000 = ["retiro", "envio_saliente"]

# CDT
MONTO_MINIMO_CDT = 500000
PLAZOS_CDT_VALIDOS = (6, 12, 18, 24, 30, 36)  # solo de 6 en 6, mín 6 máx 36
TASAS_CDT: dict[int, float] = {
    6: 0.085,   # 8.5 % E.A.
    12: 0.095,  # 9.5 % E.A.
    18: 0.10,   # 10.0 % E.A.
    24: 0.105,  # 10.5 % E.A.
    30: 0.11,   # 11.0 % E.A.
    36: 0.115,  # 11.5 % E.A.
}

# Divisas
MONEDAS = ["COP", "USD", "EUR"]
TASAS_DE_CAMBIO = {
    ("COP", "USD"): 0.00025,
    ("USD", "COP"): 4000,
    ("COP", "EUR"): 0.000244140625,
    ("EUR", "COP"): 4096,
}

# Tipos de transacciones
TIPOS_GASTO = ["retiro", "envio_saliente", "recarga_civica"]
TIPOS_INGRESO = ["deposito", "envio_entrante", "cobro_cdt"]
