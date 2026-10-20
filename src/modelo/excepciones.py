class BilleteraError(ValueError):

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
    Guarda cuánto había y cuánto se necesitaba."""

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
    """Los datos para abrir un CDT no cumplen las reglas (monto mínimo o plazo)."""

    def __init__(self, mensaje: str = "Los datos del CDT no son válidos"):
        super().__init__(mensaje)


class DivisaNoSoportadaError(BilleteraError):
    """El par de divisas solicitado no tiene tasa de cambio registrada."""

    def __init__(self, mensaje: str = "La tasa de cambio es incorrecta", par: tuple = None):
        self.par = par
        super().__init__(mensaje)


class OperacionNoPermitidaError(BilleteraError):
    """La operación existe pero no está permitida de esa forma."""

    def __init__(self, mensaje: str = "Operación no permitida"):
        super().__init__(mensaje)


class TarjetaNoExisteError(BilleteraError):
    """Se intentó operar con una tarjeta que no está registrada en la billetera."""

    def __init__(self, mensaje: str = "La tarjeta no existe", numero: int = None):
        self.numero = numero
        super().__init__(mensaje)


class TarjetaDuplicadaError(BilleteraError):
    """Se intentó crear una segunda tarjeta del mismo tipo en una billetera."""

    def __init__(self, mensaje: str = "Ya existe una tarjeta de este tipo", tipo: str = None):
        self.tipo = tipo
        super().__init__(mensaje)


# ----------------------------------------------------------------------
# Usuarios y cuentas (QUENI)
# ----------------------------------------------------------------------

class UsuarioDuplicadoError(BilleteraError):
    """Se intentó registrar un documento que ya existe."""

    def __init__(self, mensaje: str = "Ya existe un usuario con ese documento", documento: str = None):
        self.documento = documento
        super().__init__(mensaje)


class UsuarioNoExisteError(BilleteraError):
    """Se buscó un documento que no está registrado."""

    def __init__(self, mensaje: str = "El usuario no existe", documento: str = None):
        self.documento = documento
        super().__init__(mensaje)


class CuentaNoExisteError(BilleteraError):
    """Se buscó un número de cuenta que no existe."""

    def __init__(self, mensaje: str = "La cuenta no existe", numero_cuenta: int = None):
        self.numero_cuenta = numero_cuenta
        super().__init__(mensaje)
