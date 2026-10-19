"""QUENI - versión web (Flask). Ejecutar:  pip install flask  &&  python app.py"""
from dataclasses import dataclass, asdict

from flask import Flask, jsonify, render_template


# ---------- Modelos (POO) ----------
@dataclass
class Cuenta:
    tipo: str = "tipo"
    llave: str = "llave cuenta"


@dataclass
class Bolsillo:
    nombre: str = "Nombre Bolsillo"
    disponible: str = "$xxx.xxx"


@dataclass
class TarjetaBancaria:
    numero: str = "XXXX-XXXX-XXXX-XXXX"
    expira: str = "XX/XX"
    cvv: str = "XXX"
    titular: str = "NOMBRE TITULAR"


@dataclass
class TarjetaCivica:
    titular: str = "NOMBRE TITULAR CIVICA"
    cc: str = "C.C XXXXXXXX"
    civica: str = "Civ. XXXXXXXX"


@dataclass
class CDT:
    tipo: str = "tipo"
    numero: str = "xxxxxxxx"
    unidades: int = 0
    valor_unidad: str = "$0"


# ---------- Servicio: aquí se conectará el backend / base de datos ----------
class ServicioQueni:
    def __init__(self):
        self.usuario = "nombre de usuario"
        self.cuenta = Cuenta()
        self.bolsillo = Bolsillo()
        self.bolsillo_extranjero = Bolsillo()
        self.tarjeta = TarjetaBancaria()
        self.civica = TarjetaCivica()
        self.cdt = CDT()

    def estado(self):
        return {
            "usuario": self.usuario,
            "cuenta": asdict(self.cuenta),
            "bolsillo": asdict(self.bolsillo),
            "bolsillo_extranjero": asdict(self.bolsillo_extranjero),
            "tarjeta": asdict(self.tarjeta),
            "civica": asdict(self.civica),
            "cdt": asdict(self.cdt),
        }

    def ejecutar(self, accion):
        # TODO: lógica real (enviar, sacar, bolsillos...)
        return {"ok": True, "mensaje": f"{accion.replace('_', ' ').capitalize()} (sin backend aún)"}


app = Flask(__name__)
servicio = ServicioQueni()
ACCIONES = {"enviar", "sacar", "enviar_a_bolsillo", "sacar_de_bolsillo"}


@app.get("/")
def inicio():
    return render_template("index.html")


@app.get("/api/estado")
def estado():
    return jsonify(servicio.estado())


@app.post("/api/<accion>")
def accion(accion):
    if accion not in ACCIONES:
        return jsonify(ok=False, mensaje="Acción desconocida"), 404
    return jsonify(servicio.ejecutar(accion))


if __name__ == "__main__":
    app.run(debug=True)
