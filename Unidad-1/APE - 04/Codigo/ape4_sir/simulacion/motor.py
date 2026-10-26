"""Autor: Bryan Troya. Motor de pasos temporizados con SimPy."""
from dataclasses import dataclass
from random import Random

from config import ParametrosSIR
from modelo.poblacion import contar_estados, crear_poblacion, validar_poblacion
from modelo.transiciones import avanzar_paso


@dataclass(frozen=True)
class Registro:
    tiempo: int
    susceptibles: int
    infectados: int
    recuperados: int
    nuevos_contagios: int = 0
    nuevas_recuperaciones: int = 0


@dataclass
class ResultadoSIR:
    parametros: ParametrosSIR
    registros: list[Registro]

    def validar(self) -> None:
        p = self.parametros
        if len(self.registros) != p.pasos + 1:
            raise AssertionError("El numero de registros no corresponde a pasos + 1.")
        anterior: Registro | None = None
        for t, r in enumerate(self.registros):
            if r.tiempo != t:
                raise AssertionError(f"Tiempo faltante: {r.tiempo} != {t}")
            if min(r.susceptibles, r.infectados, r.recuperados) < 0:
                raise AssertionError("Existen conteos negativos.")
            if r.susceptibles + r.infectados + r.recuperados != p.poblacion:
                raise AssertionError("No se conserva N = S+I+R.")
            if anterior:
                if r.susceptibles > anterior.susceptibles:
                    raise AssertionError("Los susceptibles no pueden aumentar.")
                if r.recuperados < anterior.recuperados:
                    raise AssertionError("Los recuperados no pueden disminuir.")
                if anterior.susceptibles - r.susceptibles != r.nuevos_contagios:
                    raise AssertionError("Inconsistencia en nuevos contagios.")
                if r.recuperados - anterior.recuperados != r.nuevas_recuperaciones:
                    raise AssertionError("Inconsistencia en nuevas recuperaciones.")
            anterior = r


def ejecutar(parametros: ParametrosSIR) -> ResultadoSIR:
    """Simula con SimPy de t=0 a t=pasos, con estado propio en cada llamada."""
    try:
        import simpy
    except ImportError as exc:
        raise RuntimeError(
            "Falta SimPy. Instale las dependencias con: "
            "python -m pip install -r requirements.txt"
        ) from exc

    rng = Random(parametros.semilla)
    poblacion = crear_poblacion(
        parametros.poblacion, parametros.infectados_iniciales, rng
    )
    registros: list[Registro] = []

    def registrar(tiempo: int, contagios: int = 0, recuperaciones: int = 0) -> None:
        validar_poblacion(poblacion, parametros.poblacion)
        s, i, r = contar_estados(poblacion)
        registros.append(Registro(tiempo, s, i, r, contagios, recuperaciones))

    def paso(tiempo: int) -> None:
        nonlocal poblacion
        poblacion, eventos = avanzar_paso(
            poblacion, parametros.beta, parametros.gamma, rng,
            parametros.contactos_por_infectado,
        )
        registrar(tiempo, eventos.nuevos_contagios, eventos.nuevas_recuperaciones)

    registrar(0)
    entorno = simpy.Environment()

    def proceso_sir():
        for tiempo in range(1, parametros.pasos + 1):
            yield entorno.timeout(1)
            paso(tiempo)

    proceso = entorno.process(proceso_sir())
    entorno.run(until=proceso)

    resultado = ResultadoSIR(parametros, registros)
    resultado.validar()
    return resultado
