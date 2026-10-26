"""Autor: Wilson Palma. Construccion y contabilizacion de la poblacion SIR."""
from enum import IntEnum
from random import Random
from typing import Sequence


class Estado(IntEnum):
    SUSCEPTIBLE = 0
    INFECTADO = 1
    RECUPERADO = 2


def crear_poblacion(total: int, infectados_iniciales: int, rng: Random) -> list[Estado]:
    """Crea N agentes y selecciona aleatoriamente I0 individuos infectados."""
    if total < 1 or not 0 <= infectados_iniciales <= total:
        raise ValueError("Poblacion o infectados iniciales invalidos.")
    poblacion = [Estado.SUSCEPTIBLE] * total
    for indice in rng.sample(range(total), infectados_iniciales):
        poblacion[indice] = Estado.INFECTADO
    return poblacion


def contar_estados(poblacion: Sequence[Estado]) -> tuple[int, int, int]:
    """Devuelve (susceptibles, infectados, recuperados)."""
    return (
        sum(estado == Estado.SUSCEPTIBLE for estado in poblacion),
        sum(estado == Estado.INFECTADO for estado in poblacion),
        sum(estado == Estado.RECUPERADO for estado in poblacion),
    )


def validar_poblacion(poblacion: Sequence[Estado], total: int) -> None:
    if len(poblacion) != total:
        raise AssertionError(f"Longitud invalida: {len(poblacion)} != {total}")
    if any(estado not in Estado for estado in poblacion):
        raise AssertionError("Existe un estado de agente desconocido.")
    if sum(contar_estados(poblacion)) != total:
        raise AssertionError("No se conserva la poblacion.")
