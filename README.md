# 💳 Billetera Digital

Proyecto del curso de **Algoritmos y programación orientada a objetos**: una billetera digital simulada al estilo Nequi/Nu, construida en Python con Programación Orientada a Objetos (POO) — clases planas, sin herencia, encapsulamiento, abstracción ni polimorfismo (ver [Principios de diseño](#principios-de-diseño)).

## 📖 Descripción

La aplicación le permite a un usuario manejar su dinero a través de un disponible general y de **bolsillos** ("cajitas") de ahorro. El usuario puede guardar y retirar dinero, enviarlo a otros usuarios, moverlo entre sus propios bolsillos, solicitar tarjetas débito y/o crédito, abrir un CDT, cambiar divisas, recargar su tarjeta Cívica, y consultar tanto el historial de transacciones como estadísticas y predicciones sobre sus finanzas.

## ✨ Funcionalidades (14 requerimientos)

| # | Requerimiento |
|---|---|
| R1 | Crear un bolsillo |
| R2 | Guardar dinero (depositar) |
| R3 | Retirar dinero |
| R4 | Enviar dinero a otro usuario |
| R5 | Mover dinero entre bolsillos |
| R6 | Consultar disponible |
| R7 | Crear tarjeta (débito y/o crédito) |
| R8 | Crear un CDT |
| R9 | Consultar historial de transacciones |
| R10 | Realizar cambio de divisas |
| R11 | Calcular ahorro mensual sugerido según metas |
| R12 | Recargar tarjeta Cívica |
| R13 | Predecir gastos e ingresos futuros, con alerta de riesgo |
| R14 | Consultar estadísticas del usuario (gasto, ingresos, transacciones por mes, por categoría) |

Cada retiro y cada envío aplica automáticamente el impuesto del **4x1000** en caso de haber superado el tope mensual, y cada bolsillo genera una rentabilidad del **7% efectivo anual** sobre el saldo que mantiene guardado.

## 🧱 Modelo de dominio

6 clases: `Usuario`, `Billetera`, `Bolsillo`, `Tarjeta`, `CDT` y `Transaccion`. El detalle de atributos, métodos y relaciones está en:
- [`docs/analisis_del_problema.docx`](docs/analisis_del_problema.docx) — análisis del problema completo (requerimientos, mundo del problema, asignación de responsabilidades).
- [`docs/diagrama_de_clases.png`](docs/diagrama_de_clases.png) — diagrama de clases UML.

## 📁 Estructura del proyecto

```
billetera_digital/
├── README.md
├── requirements.txt
├── main.py             # menu de consola, los 14 requerimientos
├── src/
│   ├── __init__.py
│   ├── constantes.py   # tasas, 4x1000, categorias de gasto
│   └── modelo/
│       ├── __init__.py
│       ├── usuario.py
│       ├── billetera.py
│       ├── bolsillo.py
│       ├── tarjeta.py
│       ├── cdt.py
│       └── transaccion.py
├── tests/
│   ├── __init__.py
│   ├── test_1.py
│   ├── test_2.py
│   ├── test_3.py
└── docs/
    ├── analisis_del_problema.docx
    └── diagrama_de_clases.png
```

## 🚀 Cómo ejecutar

```bash
git clone <url-del-repositorio>
cd billetera_digital
python3 main.py
```

**Requisitos:** Python 3.10 o superior. El proyecto funciona **sin instalar nada adicional** (solo usa `datetime`, `statistics` y `random` de la librería estándar). Si quieren las mejoras opcionales (fechas exactas con `python-dateutil`, tasas de cambio en vivo con `requests`, o gráficos con `matplotlib`), instalen:







