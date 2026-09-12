# 💳 Billetera Digital

Proyecto del curso de **Fundamentos de Programación**: una billetera digital simulada al estilo Nequi/Nu, construida en Python con Programación Orientada a Objetos (POO) — clases planas, sin herencia, encapsulamiento, abstracción ni polimorfismo (ver [Principios de diseño](#principios-de-diseño)).

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

Cada retiro y cada envío aplica automáticamente el impuesto del **4x1000**, y cada bolsillo genera una rentabilidad del **7% efectivo anual** sobre el saldo que mantiene guardado.

## 🧱 Modelo de dominio

6 clases: `Usuario`, `Billetera`, `Bolsillo`, `Tarjeta`, `CDT` y `Transaccion`. El detalle de atributos, métodos y relaciones está en:
- [`docs/analisis_del_problema.docx`](docs/analisis_del_problema.docx) — análisis del problema completo (requerimientos, mundo del problema, asignación de responsabilidades).
- [`docs/diagrama_de_clases.png`](docs/diagrama_de_clases.png) — diagrama de clases UML.

### Principios de diseño

El proyecto se mantiene **deliberadamente simple**, sin los cuatro pilares clásicos de la POO:

- **Sin encapsulamiento:** atributos públicos, acceso directo, sin `@property`/getters/setters.
- **Sin abstracción:** no hay clases abstractas ni interfaces.
- **Sin herencia:** cada clase es independiente (ej. `Tarjeta` no se divide en subclases; usa un atributo `tipo`).
- **Sin polimorfismo:** los comportamientos distintos se resuelven con `if`/`elif` sobre atributos como `tipo` o `categoria`.

Más contexto y la comparativa de esfuerzo frente al enfoque clásico está en [`docs/plan_de_trabajo.pdf`](docs/plan_de_trabajo.pdf).

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
│   ├── test_billetera.py
│   ├── test_bolsillo.py
│   ├── test_cdt.py
│   ├── test_tarjeta.py
│   └── test_transaccion.py
└── docs/
    ├── analisis_del_problema.docx
    ├── diagrama_de_clases.png
    └── plan_de_trabajo.pdf
```

## 🚀 Cómo ejecutar

```bash
git clone <url-del-repositorio>
cd billetera_digital
python3 main.py
```

**Requisitos:** Python 3.10 o superior. El proyecto funciona **sin instalar nada adicional** (solo usa `datetime`, `statistics` y `random` de la librería estándar). Si quieren las mejoras opcionales (fechas exactas con `python-dateutil`, tasas de cambio en vivo con `requests`, o gráficos con `matplotlib`), instalen:

```bash
pip install -r requirements.txt
```

## 🧪 Pruebas

```bash
python3 -m unittest discover tests
```

## 👥 Equipo y responsabilidades

| Integrante | Requerimientos a cargo | Clases |
|---|---|---|
| Integrante 1 | R2, R3, R6, R9 | `Billetera` (core), `Transaccion` |
| Integrante 2 | R1, R5, R8, R11, R13 | `Bolsillo`, `CDT`, `Usuario` |
| Integrante 3 | R4, R7, R10, R12, R14 | `Tarjeta` |

Cronograma completo (3 días de desarrollo + 2 de ajustes) en [`docs/plan_de_trabajo.pdf`](docs/plan_de_trabajo.pdf).

## 📌 Estado del proyecto

- [ ] R1 · Crear un bolsillo
- [ ] R2 · Guardar dinero
- [ ] R3 · Retirar dinero
- [ ] R4 · Enviar dinero
- [ ] R5 · Mover dinero entre bolsillos
- [ ] R6 · Consultar disponible
- [ ] R7 · Crear tarjeta
- [ ] R8 · Crear un CDT
- [ ] R9 · Consultar historial de transacciones
- [ ] R10 · Cambio de divisas
- [ ] R11 · Ahorro mensual sugerido
- [ ] R12 · Recargar tarjeta Cívica
- [ ] R13 · Predicciones
- [ ] R14 · Estadísticas

## 📄 Licencia

Proyecto académico — Curso de Fundamentos de Programación. Uso educativo.