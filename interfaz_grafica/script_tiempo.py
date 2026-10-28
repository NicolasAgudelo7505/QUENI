"""
Adelanta N días el universo guardado en datos/queni.pkl.

No cambia un reloj global: resta N días a todas las fechas persistidas
para que, respecto a date.today() real, todo "envejezca" N días.

Uso (con la app cerrada):
  python script_tiempo.py
  python script_tiempo.py 90
"""

from __future__ import annotations

import pickle
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

N_POR_DEFECTO = 700

BASE = Path(__file__).resolve().parent
RUTA = BASE / "datos" / "queni.pkl"

# Posibles ubicaciones del paquete `modelo` (según cómo esté armado el repo).
CANDIDATOS_SRC = [
    BASE.parent / "src",                 # QUENI/src  (lo que usa app.py)
    BASE / "src",                        # interfaz_grafica/src
    BASE.parent,                         # QUENI/  si modelo está ahí
    BASE.parent.parent / "src",          # por si el layout es otro
    BASE,                                # interfaz_grafica/ si modelo está al lado
]


def _registrar_modelo() -> Path:
    """Pone en sys.path la carpeta que contiene el paquete modelo e importa."""
    intentos: list[str] = []

    for carpeta in CANDIDATOS_SRC:
        intentos.append(str(carpeta))
        if not carpeta.is_dir():
            continue
        # Debe existir carpeta/modelo/ (paquete) o carpeta/modelo.py
        if not ((carpeta / "modelo").is_dir() or (carpeta / "modelo.py").is_file()):
            continue
        ruta = str(carpeta)
        if ruta not in sys.path:
            sys.path.insert(0, ruta)
        try:
            import modelo  # noqa: F401
            return carpeta
        except ModuleNotFoundError:
            continue

    lineas = "\n".join(f"  - {p}" for p in intentos)
    raise SystemExit(
        "No se pudo importar el paquete 'modelo'.\n"
        "Pickle necesita las mismas clases con las que se guardó el .pkl.\n\n"
        "Rutas probadas:\n"
        f"{lineas}\n\n"
        "Revisa que exista algo como:\n"
        "  QUENI/src/modelo/__init__.py\n"
        "o indica en CANDIDATOS_SRC la carpeta correcta.\n"
        f"Script en: {BASE}\n"
    )


# Registrar ANTES de cualquier pickle.load
_MODELO_EN = _registrar_modelo()


# ---------------------------------------------------------------------------
# Utilidades de fechas
# ---------------------------------------------------------------------------

def shift(valor, delta: timedelta):
    if valor is None:
        return valor
    if isinstance(valor, datetime):
        return valor - delta
    if isinstance(valor, date):
        return valor - delta
    return valor


def shift_expiracion_mm_aa(texto: str, delta: timedelta) -> str:
    if not texto or not isinstance(texto, str):
        return texto
    try:
        mes_s, aa_s = texto.strip().split("/")
        mes, aa = int(mes_s), int(aa_s)
        anio = 2000 + aa if aa < 100 else aa
        base = date(anio, mes, 28) - delta
        return f"{base.month:02d}/{base.year % 100:02d}"
    except Exception:
        return texto


# ---------------------------------------------------------------------------
# Núcleo
# ---------------------------------------------------------------------------

def adelantar(queni, n: int) -> None:
    delta = timedelta(days=n)
    cuentas = getattr(queni, "cuentas", {}) or {}

    for billetera in cuentas.values():
        for bol in (getattr(billetera, "bolsillos", {}) or {}).values():
            if hasattr(bol, "fecha_ultima_capitalizacion"):
                bol.fecha_ultima_capitalizacion = shift(
                    bol.fecha_ultima_capitalizacion, delta
                )
            if getattr(bol, "fecha_meta", None) is not None:
                bol.fecha_meta = shift(bol.fecha_meta, delta)

        for cdt in getattr(billetera, "cdts", []) or []:
            cdt.fecha_apertura = shift(cdt.fecha_apertura, delta)
            cdt.fecha_vencimiento = shift(cdt.fecha_vencimiento, delta)

        for t in getattr(billetera, "historial", []) or []:
            t.fecha = shift(t.fecha, delta)

        tarjetas = getattr(billetera, "tarjetas", {}) or {}
        deb = tarjetas.get("Debito")
        if deb is not None and getattr(deb, "fecha_expiracion", None):
            deb.fecha_expiracion = shift_expiracion_mm_aa(deb.fecha_expiracion, delta)


def resumen(queni) -> None:
    hoy = date.today()
    print(f"\nHoy (real): {hoy}")
    cuentas = getattr(queni, "cuentas", {}) or {}
    if not cuentas:
        print("  (sin cuentas en el pickle)")
        return

    for num, billetera in cuentas.items():
        print(f"\nCuenta {num}:")
        for nombre, bol in (getattr(billetera, "bolsillos", {}) or {}).items():
            fc = getattr(bol, "fecha_ultima_capitalizacion", None)
            dias = (hoy - fc).days if isinstance(fc, date) else "?"
            print(
                f"  Bolsillo '{nombre}': ultima_cap={fc}  "
                f"(~{dias} días de interés pendiente)"
            )
        for i, cdt in enumerate(getattr(billetera, "cdts", []) or []):
            vencido = cdt.fecha_vencimiento <= hoy
            print(
                f"  CDT[{i}]: apertura={cdt.fecha_apertura}  "
                f"vence={cdt.fecha_vencimiento}  vencido={vencido}"
            )


def main() -> None:
    n = N_POR_DEFECTO
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            sys.exit(
                f"Uso: python {Path(__file__).name} [días]\n"
                f"  ejemplo: python {Path(__file__).name} 90"
            )

    if n <= 0:
        sys.exit("N debe ser un entero positivo (días a adelantar).")

    if not RUTA.is_file():
        sys.exit(
            f"No existe el pickle en:\n  {RUTA}\n"
            "¿Ya corriste la app al menos una vez?"
        )

    print(f"Modelo importado desde: {_MODELO_EN}")
    print(f"Leyendo: {RUTA}")

    with open(RUTA, "rb") as f:
        queni = pickle.load(f)

    backup = RUTA.with_suffix(f".pkl.bak_antes_de_{n}d")
    backup.write_bytes(RUTA.read_bytes())
    print(f"Backup:  {backup}")

    adelantar(queni, n)

    with open(RUTA, "wb") as f:
        pickle.dump(queni, f)

    print(f"OK: se adelantaron {n} días en el universo del pickle.")
    resumen(queni)


if __name__ == "__main__":
    main()
