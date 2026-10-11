"""
excepciones.py

Excepciones personalizadas de la billetera digital.

Jerarquía:

    ValueError                      (excepción estándar de Python)
    └── BilleteraError              (base de TODAS las excepciones del proyecto)
        ├── MontoInvalidoError
        ├── SaldoInsuficienteError
        ├── BolsilloNoExisteError
        ├── BolsilloDuplicadoError
        ├── MetaInvalidaError
        ├── MetaNoDefinidaError
        ├── MetaVencidaError
        ├── CDTInvalidoError
        ├── DivisaNoSoportadaError
        ├── OperacionNoPermitidaError
        └── TarjetaNoExisteError

¿Por qué heredan de ValueError y no directamente de Exception?
Porque así el código que ya existía (los tests y el menú, que hacen
`except ValueError`) sigue funcionando sin cambiar nada, y a la vez
ahora se puede capturar de forma más específica:

    except SaldoInsuficienteError   -> solo errores de saldo
    except BilleteraError           -> cualquier error propio del proyecto
    except ValueError               -> sigue funcionando como antes

Este archivo no importa nada del resto del paquete, por eso cualquier
otro módulo puede importarlo sin riesgo de imports circulares.
"""


class BilleteraError(ValueError):
    """Excepción base de todo el proyecto. Capturarla atrapa cualquier
    error de negocio de la billetera digital."""

    def __init__(self, mensaje: str = "Error en la billetera"):
        self.mensaje = mensaje
        super().__init__(mensaje)


# ----------------------------------------------------------------------
# Montos y saldos
# ----------------------------------------------------------------------

class MontoInvalidoError(BilleteraError):
    """El monto ingresado no es válido (cero o negativo)."""

    def __init__(self, mensaje: str = "El monto debe ser mayor a cero"):
        super().__init__(mensaje)


class SaldoInsuficienteError(BilleteraError):
    """No hay dinero suficiente en el disponible o en un bolsillo.

    Además del mensaje, guarda cuánto había y cuánto se necesitaba,
    para que quien capture el error pueda usar esos datos.
    """

    def __init__(self, mensaje: str = "Saldo insuficiente", saldo: float = None, requerido: float = None):
        self.saldo = saldo
        self.requerido = requerido
        super().__init__(mensaje)


# ----------------------------------------------------------------------
# Bolsillos y metas
# ----------------------------------------------------------------------

class BolsilloNoExisteError(BilleteraError):
    """Se intentó usar un bolsillo que no existe."""

    def __init__(self, mensaje: str = "El bolsillo no existe", nombre: str = None):
        self.nombre = nombre
        super().__init__(mensaje)


class BolsilloDuplicadoError(BilleteraError):
    """Se intentó crear un bolsillo con un nombre que ya existe."""

    def __init__(self, mensaje: str = "Ya existe un bolsillo con este nombre", nombre: str = None):
        self.nombre = nombre
        super().__init__(mensaje)


class MetaInvalidaError(BilleteraError):
    """Los datos de la meta de ahorro son inválidos (incompletos,
    monto no positivo o fecha en el pasado)."""

    def __init__(self, mensaje: str = "La meta de ahorro no es válida"):
        super().__init__(mensaje)


class MetaNoDefinidaError(BilleteraError):
    """Se pidió un cálculo de meta sobre un bolsillo que no tiene meta."""

    def __init__(self, mensaje: str = "El bolsillo no tiene una meta definida"):
        super().__init__(mensaje)


class MetaVencidaError(BilleteraError):
    """La fecha meta del bolsillo ya pasó."""

    def __init__(self, mensaje: str = "La fecha meta ya venció"):
        super().__init__(mensaje)


# ----------------------------------------------------------------------
# CDT, divisas, tarjetas y operaciones en general
# ----------------------------------------------------------------------

class CDTInvalidoError(BilleteraError):
    """Los datos para abrir un CDT no cumplen las reglas (monto mínimo
    o plazo)."""

    def __init__(self, mensaje: str = "Los datos del CDT no son válidos"):
        super().__init__(mensaje)


class DivisaNoSoportadaError(BilleteraError):
    """El par de divisas solicitado no tiene tasa de cambio registrada."""

    def __init__(self, mensaje: str = "La tasa de cambio es incorrecta", par: tuple = None):
        self.par = par
        super().__init__(mensaje)


class OperacionNoPermitidaError(BilleteraError):
    """La operación existe pero no está permitida de esa forma
    (por ejemplo, mover dinero a un bolsillo de divisa con el método
    equivocado)."""

    def __init__(self, mensaje: str = "Operación no permitida"):
        super().__init__(mensaje)


class TarjetaNoExisteError(BilleteraError):
    """Se intentó operar con una tarjeta que no está registrada."""

    def __init__(self, mensaje: str = "La tarjeta no existe", numero: int = None):
        self.numero = numero
        super().__init__(mensaje)
