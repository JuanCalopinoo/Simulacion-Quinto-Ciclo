"""Modelo determinista de índice de lluvia definido por la guía APE 001.

No es un modelo meteorológico calibrado: las etiquetas corresponden
únicamente a los umbrales fijados por la actividad académica.
"""

from dataclasses import dataclass
import numpy as np


TEMPERATURAS_TABLA = np.arange(10.0, 29.0, 2.0)
FACTORES_TABLA = np.arange(1.0, 0.0, -0.1)


@dataclass(frozen=True)
class ConfiguracionModelo:
    nombre: str
    peso_humedad: float
    peso_nubosidad: float
    peso_temperatura: float

    def __post_init__(self):
        pesos = np.array(
            [self.peso_humedad, self.peso_nubosidad, self.peso_temperatura],
            dtype=float,
        )
        if not np.all(np.isfinite(pesos)) or np.any(pesos < 0):
            raise ValueError("Los pesos deben ser finitos y no negativos.")
        if not np.isclose(np.sum(pesos), 1.0, atol=1e-10):
            raise ValueError("La suma de los pesos debe ser igual a 1.")


MODELO_ORIGINAL = ConfiguracionModelo("Original", 0.50, 0.30, 0.20)
MODELO_AJUSTADO = ConfiguracionModelo("Ajustado", 0.60, 0.30, 0.10)


def factor_temperatura(temperaturas):
    """Interpola linealmente entre valores tabulados (p. ej. 15 °C -> 0.75).

    Para temperaturas <=10 °C devuelve 1.0 y para >=28 °C, 0.1.
    No hay regla explícita para temperaturas impares en la guía;
    la interpolación es una decisión del proyecto, documentada.
    """
    t = np.asarray(temperaturas, dtype=float)
    if not np.all(np.isfinite(t)):
        raise ValueError("Las temperaturas deben ser finitas.")
    return np.interp(t, TEMPERATURAS_TABLA, FACTORES_TABLA)


def clasificar_indice(indices):
    """Convierte índices [0, 1] a los cuatro estados de la guía."""
    i = np.asarray(indices, dtype=float)
    if not np.all(np.isfinite(i)) or np.any(i < -1e-10) or np.any(i > 1 + 1e-10):
        raise ValueError("Los índices deben estar entre 0 y 1.")
    return np.select(
        [i < 0.40, i < 0.60, i < 0.75],
        ["Sin lluvia", "Baja posibilidad", "Lluvia probable"],
        default="Lluvia",
    )


def calcular_modelo(humedad, nubosidad, temperatura, configuracion=MODELO_ORIGINAL):
    """Calcula factores, contribuciones ponderadas, índices y estados."""
    humedad = np.asarray(humedad, dtype=float)
    nubosidad = np.asarray(nubosidad, dtype=float)
    temperatura = np.asarray(temperatura, dtype=float)
    if not (humedad.shape == nubosidad.shape == temperatura.shape):
        raise ValueError("Los vectores deben tener la misma longitud.")
    if not (np.all(np.isfinite(humedad)) and np.all(np.isfinite(nubosidad))):
        raise ValueError("Humedad y nubosidad deben ser finitas.")
    if np.any((humedad < 0) | (humedad > 100)) or np.any((nubosidad < 0) | (nubosidad > 100)):
        raise ValueError("Humedad y nubosidad deben variar de 0 a 100 %.")
    h = humedad / 100.0
    n = nubosidad / 100.0
    tf = factor_temperatura(temperatura)
    ch = configuracion.peso_humedad * h
    cn = configuracion.peso_nubosidad * n
    ct = configuracion.peso_temperatura * tf
    indice = ch + cn + ct
    return {
        "H": h, "N": n, "Tf": tf,
        "contribucion_h": ch, "contribucion_n": cn, "contribucion_tf": ct,
        "indice": indice, "estado": clasificar_indice(indice),
    }
