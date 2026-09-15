# Billetera Digital

La aplicación le permite a un usuario manejar su dinero a través de un disponible general y de **bolsillos** ("cajitas") de ahorro. El usuario puede guardar y retirar dinero, enviarlo a otros usuarios, moverlo entre sus propios bolsillos, solicitar tarjetas débito y/o Civica, abrir un CDT, cambiar divisas, recargar su tarjeta Cívica, y consultar tanto el historial de transacciones como estadísticas y predicciones sobre sus finanzas.

## Funcionalidades (14 requerimientos)

| # | Requerimiento                                                                              |
|---|--------------------------------------------------------------------------------------------|
| R1 | Crear un bolsillo                                                                          |
| R2 | Guardar dinero (depositar)                                                                 |
| R3 | Retirar dinero                                                                             |
| R4 | Enviar dinero a otro usuario                                                               |
| R5 | Mover dinero entre bolsillos                                                               |
| R6 | Consultar disponible                                                                       |
| R7 | Crear tarjeta (débito y/o Civica)                                                          |
| R8 | Crear un CDT                                                                               |
| R9 | Consultar historial de transacciones                                                       |
| R10 | Realizar cambio de divisas                                                                 |
| R11 | Calcular ahorro mensual sugerido según metas                                               |
| R12 | Recargar tarjeta Cívica                                                                    |
| R13 | Predecir gastos e ingresos futuros, con alerta de riesgo                                   |
| R14 | Consultar estadísticas del usuario (gasto, ingresos, transacciones por mes) |

Cada retiro y cada envío aplica automáticamente el impuesto del **4x1000** en caso de haber superado el tope mensual, y cada bolsillo genera una rentabilidad del **7% efectivo anual** sobre el saldo que mantiene guardado.


## Estructura del proyecto

```
billetera_digital/
├── README.md
├── Diagrama.txt
├── main.py 
├── .gitignore            
├── src/
│   └── modelo/
│       ├── __init__.py
│       ├── usuario.py
│       ├── billetera.py
│       ├── bolsillo.py
│       ├── tarjeta.py
│       ├── cdt.py
│       ├── constantes.py  
│       └── transaccion.py
├── tests/
│   ├── __init__.py
│   ├── test1.py
│   ├── test2.py
│   ├── test3.py
│   └── test4.py
└── docs/
    ├── Analisis_Billetera_Digital.docx
    ├── diagrama_clases_drawio.png
    ├── Link_diagrama_clases.txt
    └── Pantallas QUENI.pdf
```

**Requisitos:** Python 3.10 o superior. El proyecto funciona **sin instalar nada adicional** (solo usa `datetime`, `statistics` y `random` de la librería estándar). 







