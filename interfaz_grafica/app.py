"""QUENI - versión web (Flask).

Ejecutar:  pip install flask  &&  python app.py

Capas:
  - queni/          dominio (reglas de negocio, sin nada de web)
  - ServicioQueni   traduce peticiones web -> llamadas al dominio (este archivo)
  - Flask           rutas HTTP/JSON que consume templates/index.html
"""
import math
import os
import sys
import pickle
import re
import secrets
import threading
from datetime import date
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import Flask, Response, jsonify, render_template, request, session
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from modelo import QUENI, AnalizadorFinanciero, Civica, Usuario, constantes
from modelo.excepciones import (
    BilleteraError,
    SaldoInsuficienteError,
    UsuarioNoExisteError,
)

DATOS = Path(__file__).with_name("datos")
ARCHIVO_DATOS = DATOS / "queni.pkl"
MONTO_MAXIMO = 1e13

Datos = dict[str, Any]                       # cuerpo JSON de una petición
Respuesta = Response | tuple[Response, int]  # lo que devuelve una vista de Flask


# ---------- Errores propios de la capa web ----------
class DatoInvalidoError(BilleteraError):
    """Un dato de la petición falta o no tiene el formato esperado."""


class SesionExpirada(Exception):
    """La sesión apunta a un usuario que ya no existe."""


# ---------- Utilidades de formato y validación ----------
def cop(valor: float) -> str:
    return "$" + f"{round(valor):,}".replace(",", ".")


def _monto(datos: Datos, campo: str = "monto", etiqueta: str = "El monto") -> float:
    valor = datos.get(campo)
    if valor is None or valor == "":
        raise DatoInvalidoError(f"{etiqueta} es obligatorio")
    if isinstance(valor, bool):
        raise DatoInvalidoError(f"{etiqueta} debe ser un número")
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise DatoInvalidoError(f"{etiqueta} debe ser un número")
    if not math.isfinite(numero) or numero > MONTO_MAXIMO:
        raise DatoInvalidoError(f"{etiqueta} no es válido")
    return round(numero, 2)


def _monto_opcional(datos: Datos, campo: str, etiqueta: str) -> float | None:
    if datos.get(campo) in (None, ""):
        return None
    return _monto(datos, campo, etiqueta)


def _entero(datos: Datos, campo: str, etiqueta: str, maximo: int = 10**15, minimo: int = 1) -> int:
    valor = datos.get(campo)
    if valor is None or valor == "" or isinstance(valor, bool):
        raise DatoInvalidoError(f"{etiqueta} es obligatorio")
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise DatoInvalidoError(f"{etiqueta} debe ser un número entero")
    if not math.isfinite(numero) or not numero.is_integer() or not minimo <= numero <= maximo:
        raise DatoInvalidoError(f"{etiqueta} no es válido")
    return int(numero)


def _texto(datos: Datos, campo: str, etiqueta: str, maximo: int = 60) -> str:
    valor = datos.get(campo)
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise DatoInvalidoError(f"{etiqueta} es obligatorio")
    if not isinstance(valor, str):
        raise DatoInvalidoError(f"{etiqueta} no es válido")
    valor = valor.strip()
    if len(valor) > maximo:
        raise DatoInvalidoError(f"{etiqueta} es demasiado largo (máximo {maximo} caracteres)")
    return valor


def _origen(datos: Datos) -> str | None:
    """None = disponible; cualquier texto = nombre de un bolsillo en pesos."""
    valor = datos.get("origen")
    if valor is None or valor == "":
        return None
    if not isinstance(valor, str):
        raise DatoInvalidoError("El origen no es válido")
    if valor in constantes.MONEDAS:  # los bolsillos de divisa solo se tocan con cambiar_divisas
        raise DatoInvalidoError("Ese bolsillo solo se usa al cambiar divisas")
    return valor


def _fecha(datos: Datos, campo: str, etiqueta: str) -> date | None:
    valor = datos.get(campo)
    if valor is None or valor == "":
        return None
    try:
        return date.fromisoformat(str(valor))
    except ValueError:
        raise DatoInvalidoError(f"{etiqueta} no es una fecha válida")


def _mensaje_error(error: BilleteraError) -> str:
    if isinstance(error, SaldoInsuficienteError) and error.saldo is not None and error.requerido is not None:
        return f"{error.mensaje}: tienes {cop(error.saldo)} y necesitas {cop(error.requerido)}"
    return error.mensaje


def _agrupar(numero: int | str) -> str:
    texto = str(numero)
    return "-".join(texto[i:i + 4] for i in range(0, len(texto), 4))


# ---------- Servicio: une la web con el dominio ----------
class ServicioQueni:
    def __init__(self, archivo: Path = ARCHIVO_DATOS) -> None:
        self.archivo = archivo
        self.lock = threading.RLock()
        self.queni: QUENI = self._cargar()

    # --- persistencia (pickle local; reemplazable por una base de datos) ---
    def _cargar(self) -> QUENI:
        try:
            with open(self.archivo, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return QUENI()
        except Exception:
            app.logger.exception("No se pudo leer %s; se inicia vacío", self.archivo)
            return QUENI()

    def guardar(self) -> None:
        try:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)
            temporal = self.archivo.with_suffix(".tmp")
            with open(temporal, "wb") as f:
                pickle.dump(self.queni, f)
            os.replace(temporal, self.archivo)  # escritura atómica
        except Exception:
            app.logger.exception("No se pudieron guardar los datos")

    # --- sesión ---
    def usuario(self, documento: str) -> Usuario:
        try:
            return self.queni.buscar_usuario(documento)
        except UsuarioNoExisteError:
            raise SesionExpirada()

    def registrar(self, datos: Datos) -> str:
        nombre = _texto(datos, "nombre", "El nombre")
        documento = _texto(datos, "documento", "El documento", maximo=20)
        if not re.fullmatch(r"[0-9A-Za-z]{4,20}", documento):
            raise DatoInvalidoError("El documento debe tener entre 4 y 20 letras o números")
        sueldo = _monto(datos, "sueldo", "El sueldo")
        saldo = _monto_opcional(datos, "saldo_inicial", "El saldo inicial") or 0.0

        usuario = self.queni.registrar_usuario(nombre, documento, sueldo, saldo)
        numero_cuenta = usuario.billetera.numero_cuenta
        self.queni.asignar_tarjeta_debito(numero_cuenta)
        self.queni.asignar_tarjeta_civica(numero_cuenta)
        return documento

    def ingresar(self, datos: Datos) -> str:
        documento = _texto(datos, "documento", "El documento", maximo=20)
        return self.queni.buscar_usuario(documento).documento

    # --- lectura ---
    def estado(self, documento: str) -> dict[str, Any]:
        u = self.usuario(documento)
        w = u.billetera
        ahorros = AnalizadorFinanciero(u).ahorro_mensual_sugerido()

        bolsillos: list[dict[str, Any]] = []
        extranjeros: list[dict[str, Any]] = []
        for nombre, b in w.bolsillos.items():
            if nombre in constantes.MONEDAS:
                extranjeros.append({"moneda": nombre, "saldo": b.saldo})
                continue
            bolsillos.append({
                "nombre": nombre,
                "saldo": b.saldo,
                "rendimiento_mensual": b.calcular_rendimiento_mensual(),
                "meta": (
                    {"monto": b.monto_meta, "fecha": b.fecha_meta.isoformat()}
                    if b.monto_meta is not None and b.fecha_meta is not None else None
                ),
                "ahorro": ahorros.get(nombre),
            })

        deb = w.tarjetas.get("Debito")
        civ = w.tarjetas.get("Civica")
        civ = civ if isinstance(civ, Civica) else None
        hoy = date.today()
        return {
            "usuario": {"nombre": u.nombre, "documento": u.documento, "sueldo": u.sueldo},
            "cuenta": {"tipo": "Ahorros", "llave": str(w.numero_cuenta), "disponible": w.disponible},
            "bolsillos": bolsillos,
            "extranjeros": extranjeros,
            "tasas": [{"de": a, "a": b, "tasa": t} for (a, b), t in constantes.TASAS_DE_CAMBIO.items()],
            "tarjeta": None if deb is None else {
                "numero": _agrupar(deb.numero),
                "expira": deb.fecha_expiracion,
                "cvv": deb.cvv,
                "titular": u.nombre.upper(),
            },
            "civica": None if civ is None else {
                "titular": u.nombre.upper(),
                "cc": f"C.C {u.documento}",
                "civica": f"Civ. {civ.numero}",
                "saldo": civ.saldo,
            },
            "cdts": [
                {
                    "monto": c.monto,
                    "plazo_meses": c.plazo_meses,
                    "tasa": c.tasa_interes,
                    "fecha_apertura": c.fecha_apertura.isoformat(),
                    "fecha_vencimiento": c.fecha_vencimiento.isoformat(),
                    "valor_proyectado": c.calcular_valor_proyectado(),
                    "vencido": hoy >= c.fecha_vencimiento,
                }
                for c in w.cdts
            ],
            "limites": {
                "monto_minimo_cdt": constantes.MONTO_MINIMO_CDT,
                "tasa_cdt": constantes.RENTABILIDAD_CDT,
                "tope_4x1000": constantes.TOPE_MENSUAL * constantes.VALOR_UVT,
                "acumulado_mes": w.calcular_acumulado_mensual(),
            },
        }

    def historial(self, documento: str, limite: int = 100) -> dict[str, Any]:
        w = self.usuario(documento).billetera
        items: list[dict[str, Any]] = []
        for t in reversed(w.historial[-limite:]):
            if t.tipo in constantes.TIPOS_GASTO:
                naturaleza = "gasto"
            elif t.tipo in constantes.TIPOS_INGRESO:
                naturaleza = "ingreso"
            else:
                naturaleza = "neutro"
            moneda = t.origen if (t.tipo == "cambio_divisa" and t.origen in constantes.MONEDAS) else "COP"
            items.append({
                "fecha": t.fecha.isoformat(),
                "tipo": t.tipo,
                "naturaleza": naturaleza,
                "monto": t.monto,
                "moneda": moneda,
                "origen": t.origen,
                "destino": t.destino,
                "impuesto": t.impuesto_4x1000,
                "tasa": t.tasa_aplicada,
                "saldo_resultante": t.saldo_resultante,
            })
        return {"items": items}

    def analisis(self, documento: str) -> dict[str, Any]:
        u = self.usuario(documento)
        analizador = AnalizadorFinanciero(u)
        hoy = date.today()
        return {
            "sueldo": u.sueldo,
            "mes": analizador.estadisticas(inicio=hoy.replace(day=1), fin=hoy),
            "total": analizador.estadisticas(),
            "proyeccion": analizador.predecir_gastos_e_ingresos(),
            "ahorros": analizador.ahorro_mensual_sugerido(),
        }

    # --- acciones: cada una devuelve el mensaje que ve la persona ---
    def _enviar(self, u: Usuario, d: Datos) -> str:
        cuenta = _entero(d, "cuenta_destino", "La cuenta destino")
        monto, origen = _monto(d), _origen(d)
        impuesto = self.queni.enviar(u.documento, cuenta, monto, origen)
        extra = f" (4x1000: {cop(impuesto)})" if impuesto else ""
        return f"Enviaste {cop(monto)}{extra}"

    def _sacar(self, u: Usuario, d: Datos) -> str:
        monto, origen = _monto(d), _origen(d)
        impuesto = u.billetera.retirar_dinero(monto, origen)
        extra = f" (4x1000: {cop(impuesto)})" if impuesto else ""
        return f"Sacaste {cop(monto)}{extra}"

    def _depositar(self, u: Usuario, d: Datos) -> str:
        monto = _monto(d)
        u.billetera.depositar_dinero(monto)
        return f"Depositaste {cop(monto)}"

    def _enviar_a_bolsillo(self, u: Usuario, d: Datos) -> str:
        """Mueve dinero a un bolsillo, desde el disponible o desde OTRO bolsillo."""
        bolsillo = _texto(d, "bolsillo", "El bolsillo de destino")
        monto, origen = _monto(d), _origen(d)
        u.billetera.mover_entre_bolsillos(bolsillo, monto, origen)
        if origen is None:
            return f"Enviaste {cop(monto)} a {bolsillo}"
        return f"Moviste {cop(monto)} de {origen} a {bolsillo}"

    def _sacar_de_bolsillo(self, u: Usuario, d: Datos) -> str:
        bolsillo = _texto(d, "bolsillo", "El bolsillo")
        monto = _monto(d)
        u.billetera.retirar_de_bolsillo(monto, bolsillo)
        return f"Sacaste {cop(monto)} de {bolsillo}"

    def _nuevo_bolsillo(self, u: Usuario, d: Datos) -> str:
        nombre = _texto(d, "nombre", "El nombre del bolsillo", maximo=30)
        monto_meta = _monto_opcional(d, "monto_meta", "La meta")
        fecha_meta = _fecha(d, "fecha_meta", "La fecha meta")
        u.billetera.crear_bolsillo(nombre, monto_meta, fecha_meta)
        return f"Bolsillo '{nombre}' creado"

    def _abrir_cdt(self, u: Usuario, d: Datos) -> str:
        monto = _monto(d)
        plazo = _entero(d, "plazo_meses", "El plazo", maximo=120)
        u.billetera.crear_cdt(monto, plazo, _origen(d))
        return f"CDT de {cop(monto)} a {plazo} meses abierto"

    def _redimir_cdt(self, u: Usuario, d: Datos) -> str:
        w = u.billetera
        indice = _entero(d, "indice", "El CDT", maximo=10**6, minimo=0)
        if indice >= len(w.cdts):
            raise DatoInvalidoError("El CDT no existe o ya fue redimido")
        cdt = w.cdts[indice]
        # Se calcula antes: al redimir, el CDT sale de la lista.
        valor_final = cdt.calcular_valor_proyectado()
        ganancia = valor_final - cdt.monto
        w.redimir_cdt(cdt)
        return f"CDT redimido: recibiste {cop(valor_final)} (ganancia {cop(ganancia)})"

    def _cambiar_divisas(self, u: Usuario, d: Datos) -> str:
        par = _texto(d, "par", "El par de monedas")
        de, _, a = par.partition(">")
        monto = _monto(d)
        # Si se convierte desde una moneda extranjera, el dinero sale de su bolsillo.
        origen = _origen(d) if de == "COP" else de
        u.billetera.cambiar_divisas(monto, (de, a), origen)
        tasa = constantes.TASAS_DE_CAMBIO[(de, a)]
        return f"Cambiaste {monto:g} {de} a {monto * tasa:,.2f} {a}"

    def _recargar_civica(self, u: Usuario, d: Datos) -> str:
        monto = _monto(d)
        w = u.billetera
        civica = w.tarjetas.get("Civica")
        w.recargar_civica(monto, civica if isinstance(civica, Civica) else None, _origen(d))
        return f"Recargaste {cop(monto)} en tu Cívica"

    def ejecutar(self, documento: str, accion: str, datos: Datos) -> str:
        return getattr(self, f"_{accion}")(self.usuario(documento), datos)


# ---------- Aplicación Flask ----------
app = Flask(__name__)


def _clave_secreta() -> str:
    """Variable de entorno, o una clave aleatoria guardada en datos/.secret."""
    clave = os.environ.get("QUENI_SECRET_KEY")
    if clave:
        return clave
    ruta = DATOS / ".secret"
    if not ruta.exists():
        DATOS.mkdir(exist_ok=True)
        ruta.write_text(secrets.token_hex(32))
        os.chmod(ruta, 0o600)
    return ruta.read_text().strip()


app.secret_key = _clave_secreta()
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

servicio = ServicioQueni()

# Nombres de ruta de las acciones que modifican dinero/datos (cada una es un método _nombre del servicio)
ACCIONES: set[str] = {
    "enviar", "sacar", "depositar",
    "enviar_a_bolsillo", "sacar_de_bolsillo", "nuevo_bolsillo",
    "abrir_cdt", "redimir_cdt", "cambiar_divisas", "recargar_civica",
}


def _ejecutar(funcion: Callable[[], dict[str, Any]], guardar: bool = False) -> Respuesta:
    """Ejecuta con candado, guarda si hubo cambios y traduce errores a JSON."""
    try:
        with servicio.lock:
            resultado = funcion()
            if guardar:
                servicio.guardar()
        return jsonify(resultado)
    except SesionExpirada:
        session.clear()
        return jsonify(ok=False, mensaje="Tu sesión expiró. Ingresa de nuevo"), 401
    except BilleteraError as error:
        return jsonify(ok=False, mensaje=_mensaje_error(error)), 400
    except Exception:
        app.logger.exception("Error inesperado")
        return jsonify(ok=False, mensaje="Error interno del servidor"), 500


def requiere_sesion(vista: Callable[..., Respuesta]) -> Callable[..., Respuesta]:
    @wraps(vista)
    def envoltura(*args: Any, **kwargs: Any) -> Respuesta:
        if "documento" not in session:
            return jsonify(ok=False, mensaje="Ingresa para continuar"), 401
        return vista(*args, **kwargs)
    return envoltura


def requiere_json(vista: Callable[..., Respuesta]) -> Callable[..., Respuesta]:
    """Solo acepta JSON: un formulario de otro sitio no puede enviarlo sin permiso (CSRF)."""
    @wraps(vista)
    def envoltura(*args: Any, **kwargs: Any) -> Respuesta:
        if not request.is_json:
            return jsonify(ok=False, mensaje="Se esperaba JSON"), 415
        return vista(*args, **kwargs)
    return envoltura


def _datos() -> Datos:
    datos = request.get_json(silent=True)
    return datos if isinstance(datos, dict) else {}


@app.get("/")
def inicio() -> str:
    return render_template("index.html")


# --- sesión ---
@app.post("/api/registro")
@requiere_json
def registro() -> Respuesta:
    def hacer() -> dict[str, Any]:
        documento = servicio.registrar(_datos())
        session.clear()
        session["documento"] = documento
        return {"ok": True, "mensaje": "Cuenta creada"}
    return _ejecutar(hacer, guardar=True)


@app.post("/api/login")
@requiere_json
def login() -> Respuesta:
    def hacer() -> dict[str, Any]:
        documento = servicio.ingresar(_datos())
        session.clear()
        session["documento"] = documento
        return {"ok": True, "mensaje": "Bienvenido"}
    return _ejecutar(hacer)


@app.post("/api/logout")
@requiere_json
def logout() -> Respuesta:
    session.clear()
    return jsonify(ok=True, mensaje="Sesión cerrada")


# --- lectura ---
@app.get("/api/estado")
@requiere_sesion
def estado() -> Respuesta:
    return _ejecutar(lambda: servicio.estado(session["documento"]))


@app.get("/api/historial")
@requiere_sesion
def historial() -> Respuesta:
    return _ejecutar(lambda: servicio.historial(session["documento"]))


@app.get("/api/analisis")
@requiere_sesion
def analisis() -> Respuesta:
    return _ejecutar(lambda: servicio.analisis(session["documento"]))


# --- acciones ---
@app.post("/api/<accion>")
@requiere_json
@requiere_sesion
def accion(accion: str) -> Respuesta:
    if accion not in ACCIONES:
        return jsonify(ok=False, mensaje="Acción desconocida"), 404

    def hacer() -> dict[str, Any]:
        mensaje = servicio.ejecutar(session["documento"], accion, _datos())
        return {"ok": True, "mensaje": mensaje}
    return _ejecutar(hacer, guardar=True)


if __name__ == "__main__":
    app.run(debug=True)