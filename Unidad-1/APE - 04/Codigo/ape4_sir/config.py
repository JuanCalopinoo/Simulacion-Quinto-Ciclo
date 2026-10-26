"""Configuracion central: todos los modulos usan los mismos parametros."""
from dataclasses import dataclass


@dataclass(frozen=True)
class ParametrosSIR:
    poblacion: int = 100
    infectados_iniciales: int = 5
    beta: float = 0.30
    gamma: float = 0.10
    pasos: int = 100
    contactos_por_infectado: int = 1
    semilla: int = 42

    def __post_init__(self) -> None:
        for nombre in ("poblacion", "infectados_iniciales", "pasos",
                       "contactos_por_infectado", "semilla"):
            if type(getattr(self, nombre)) is not int:
                raise ValueError(f"{nombre} debe ser un entero (no booleano).")
        if self.poblacion < 2:
            raise ValueError("La poblacion debe ser al menos de 2 individuos.")
        if not 0 <= self.infectados_iniciales <= self.poblacion:
            raise ValueError("Los infectados iniciales deben estar entre 0 y N.")
        if not 0 <= self.beta <= 1:
            raise ValueError("La probabilidad beta debe estar entre 0 y 1.")
        if not 0 <= self.gamma <= 1:
            raise ValueError("La probabilidad gamma debe estar entre 0 y 1.")
        if self.pasos < 0:
            raise ValueError("El numero de pasos no puede ser negativo.")
        if self.contactos_por_infectado < 1:
            raise ValueError("Se requiere al menos un contacto por infectado.")
        if self.contactos_por_infectado >= self.poblacion:
            raise ValueError("Los contactos por infectado no pueden superar N - 1.")

    @property
    def susceptibles_iniciales(self) -> int:
        return self.poblacion - self.infectados_iniciales

