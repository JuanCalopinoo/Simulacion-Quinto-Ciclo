"""Autora: Katheryn Contento. Graficos compatibles con Linux sin interfaz grafica."""
from pathlib import Path

from simulacion.motor import ResultadoSIR


def guardar_grafica(resultado: ResultadoSIR, carpeta: Path) -> Path:
    # Importaciones diferidas para poder probar el motor sin cargar Matplotlib.
    import matplotlib
    matplotlib.use("Agg")  # Funciona por terminal/SSH, sin entorno de escritorio.
    import matplotlib.pyplot as plt
    import numpy as np

    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    registros = resultado.registros
    tiempo = np.array([r.tiempo for r in registros], dtype=int)
    series = (
        ("Susceptibles", np.array([r.susceptibles for r in registros]), "#2276BA"),
        ("Infectados", np.array([r.infectados for r in registros]), "#D14A46"),
        ("Recuperados", np.array([r.recuperados for r in registros]), "#279A68"),
    )

    # Las tres curvas comparten ejes para comparar su evolución.
    fig, ax = plt.subplots(figsize=(10, 5.4), constrained_layout=True)
    for titulo, valores, color in series:
        ax.plot(tiempo, valores, label=titulo, color=color, linewidth=2.3)
    ax.set(title="Modelo SIR - evolución de la población", xlabel="Tiempo (pasos)",
           ylabel="Cantidad de individuos", xlim=(0, max(1, resultado.parametros.pasos)),
           ylim=(0, resultado.parametros.poblacion))
    ax.grid(alpha=0.25)
    ax.legend()
    ruta = carpeta / "sir_evolucion.png"
    fig.savefig(ruta, dpi=170)
    plt.close(fig)
    return ruta

