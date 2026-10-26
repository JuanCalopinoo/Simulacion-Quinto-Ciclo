"""Autor: Juan Calopino. Contagios y recuperaciones por paso discreto."""
from dataclasses import dataclass
from random import Random
from typing import Sequence

from modelo.poblacion import Estado


@dataclass(frozen=True)
class ConteoTransiciones:
    nuevos_contagios: int
    nuevas_recuperaciones: int


def avanzar_paso(
    poblacion: Sequence[Estado],
    beta: float,
    gamma: float,
    rng: Random,
    contactos_por_infectado: int = 1,
) -> tuple[list[Estado], ConteoTransiciones]:
    """Aplica un paso SIR por agentes con actualizacion simultanea.

    Cada infectado contacta k *otros* individuos, elegidos sin reposicion.
    Solo un contacto susceptible del estado anterior puede infectarse.
    Cada infectado original tiene probabilidad gamma de recuperarse.
    Nuevos infectados no contagian hasta el siguiente paso.
    """
    n = len(poblacion)
    if n < 2:
        raise ValueError("Se requieren al menos dos agentes.")
    if not 0 <= beta <= 1 or not 0 <= gamma <= 1:
        raise ValueError("Las probabilidades deben estar entre 0 y 1.")
    if not 1 <= contactos_por_infectado < n:
        raise ValueError("Los contactos deben estar en [1, N-1].")

    siguiente = list(poblacion)
    contagios = 0
    recuperaciones = 0

    # Se recorre el estado anterior, nunca los estados recien modificados.
    for i, estado in enumerate(poblacion):
        if estado != Estado.INFECTADO:
            continue

        # Candidatos: todos los demas agentes, no solamente susceptibles.
        # Eso hace que la probabilidad de encontrar un susceptible dependa de S/N.
        contactos = rng.sample(range(n - 1), contactos_por_infectado)
        for contacto in contactos:
            j = contacto if contacto < i else contacto + 1
            if poblacion[j] == Estado.SUSCEPTIBLE and rng.random() < beta:
                if siguiente[j] == Estado.SUSCEPTIBLE:
                    siguiente[j] = Estado.INFECTADO
                    contagios += 1

        if rng.random() < gamma:
            siguiente[i] = Estado.RECUPERADO
            recuperaciones += 1

    return siguiente, ConteoTransiciones(contagios, recuperaciones)
