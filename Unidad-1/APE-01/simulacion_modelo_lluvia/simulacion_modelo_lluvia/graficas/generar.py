"""Gráficas automáticas de los nueve registros observados en la guía."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

AZUL = "#193A5C"
CELESTE = "#167D95"
NARANJA = "#E28A32"
VERDE = "#409470"
GRIS = "#6B7280"
ROJO = "#C95854"


def _crear(figsize=(11, 5.6)):
    fig, ax = plt.subplots(figsize=figsize, layout="constrained")
    fig.patch.set_facecolor("white")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.17, zorder=0)
    ax.set_axisbelow(True)
    return fig, ax


def _horas(ax, horas, posiciones):
    ax.set_xticks(posiciones, horas)
    ax.set_xlabel("Hora de medición")


def generar_graficas(datos, resultados, salida, mostrar=False):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    horas = datos["hora"]
    x = np.arange(len(horas))
    orig, ajust = resultados["original"], resultados["ajustado"]
    rutas = []

    # 1. Dos escalas en ejes separados: nunca superponer temperaturas a porcentajes.
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.3), sharex=True,
                                   layout="constrained", gridspec_kw={"height_ratios": [1.3, 1]})
    fig.patch.set_facecolor("white")
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(alpha=.16)
    ax1.plot(x, datos["humedad"], "-o", color=CELESTE, lw=2.3, label="Humedad")
    ax1.plot(x, datos["nubosidad"], "-s", color=NARANJA, lw=2.3, label="Nubosidad")
    ax1.set_ylabel("Porcentaje (%)")
    ax1.set_ylim(0, 105)
    ax1.legend(loc="upper left", ncol=2, frameon=False)
    ax1.set_title("01 | Evolución de las variables atmosféricas", fontsize=15, weight="bold", loc="left", pad=16)
    ax2.plot(x, datos["temperatura"], "-D", color=ROJO, lw=2.3, label="Temperatura")
    ax2.set_ylim(10, 26)
    ax2.set_ylabel("Temperatura (°C)")
    ax2.set_xlabel("Hora de medición")
    ax2.set_xticks(x, horas)
    fig.savefig(salida / "01_variables_atmosfericas.png", dpi=175)
    rutas.append(salida / "01_variables_atmosfericas.png")
    if not mostrar:
        plt.close(fig)

    # 2. Normalizados, comparables en una misma escala.
    fig, ax = _crear()
    for clave, etiqueta, color, estilo in [("H", "Humedad H", CELESTE, "o"),
                                          ("N", "Nubosidad N", NARANJA, "s"),
                                          ("Tf", "Temperatura Tf", VERDE, "D")]:
        ax.plot(x, orig[clave], marker=estilo, lw=2.1, color=color, label=etiqueta)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Valor normalizado (0 a 1)")
    ax.set_title("02 | Factores normalizados del modelo", fontsize=15, weight="bold", loc="left", pad=16)
    _horas(ax, horas, x)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.savefig(salida / "02_factores_normalizados.png", dpi=175)
    rutas.append(salida / "02_factores_normalizados.png")
    if not mostrar:
        plt.close(fig)

    # 3. Bandas y fronteras según reglas de la guía.
    fig, ax = _crear(figsize=(11, 6.4))
    ax.axhspan(0, .4, color="#F1F5F9", alpha=1, zorder=-2)
    ax.axhspan(.4, .6, color="#FDEFD7", alpha=.75, zorder=-2)
    ax.axhspan(.6, .75, color="#DCEFEB", alpha=.9, zorder=-2)
    ax.axhspan(.75, 1, color="#D2E4EE", alpha=.82, zorder=-2)
    ax.plot(x, orig["indice"], "-o", color=AZUL, lw=2.5, ms=8, label="Índice original")
    for umbral in (.4, .6, .75):
        ax.axhline(umbral, ls="--", lw=1.1, color=GRIS, alpha=.7)
    for j, valor in enumerate(orig["indice"]):
        ax.annotate(f"{valor:.3f}", (j, valor), xytext=(0, 10),
                    textcoords="offset points", ha="center", fontsize=9)
    ax.set_ylim(0, 1.04)
    ax.set_ylabel("Índice I (0 a 1)")
    ax.set_title("03 | Índice original y umbrales de clasificación", fontsize=15,
                 weight="bold", loc="left", pad=16)
    _horas(ax, horas, x)
    ax.legend(loc="lower right", frameon=False)
    fig.savefig(salida / "03_indice_y_umbrales.png", dpi=175)
    rutas.append(salida / "03_indice_y_umbrales.png")
    if not mostrar:
        plt.close(fig)

    # 4. Contribución real por variable a I(t).
    fig, ax = _crear(figsize=(11, 6.0))
    ax.bar(x, orig["contribucion_h"], color=CELESTE, width=.65, label="0.5 × H")
    ax.bar(x, orig["contribucion_n"], bottom=orig["contribucion_h"], color=NARANJA,
           width=.65, label="0.3 × N")
    ax.bar(x, orig["contribucion_tf"], bottom=orig["contribucion_h"] + orig["contribucion_n"],
           color=VERDE, width=.65, label="0.2 × Tf")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Aporte al índice")
    ax.set_title("04 | Influencia de los componentes en el modelo original", fontsize=15,
                 weight="bold", loc="left", pad=16)
    _horas(ax, horas, x)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    fig.savefig(salida / "04_aportes_del_modelo.png", dpi=175)
    rutas.append(salida / "04_aportes_del_modelo.png")
    if not mostrar:
        plt.close(fig)

    # 5. Comparación de escenarios y visualización del efecto del ajuste.
    fig, ax = _crear(figsize=(11, 6.1))
    ax.plot(x, orig["indice"], "-o", lw=2.3, color=AZUL, label="Original (0.5 / 0.3 / 0.2)")
    ax.plot(x, ajust["indice"], "--s", lw=2.3, color=ROJO,
            label="Ajustado (0.6 / 0.3 / 0.1)")
    ax.fill_between(x, orig["indice"], ajust["indice"], color=ROJO, alpha=.12)
    for umbral in (.4, .6, .75):
        ax.axhline(umbral, color=GRIS, ls=":", lw=1)
    ax.set_ylim(.3, 1.0)
    ax.set_ylabel("Índice I")
    ax.set_title("05 | Comparación: modelo original frente al ajustado", fontsize=15,
                 weight="bold", loc="left", pad=16)
    _horas(ax, horas, x)
    ax.legend(frameon=False, loc="upper left")
    fig.savefig(salida / "05_comparacion_escenarios.png", dpi=175)
    rutas.append(salida / "05_comparacion_escenarios.png")
    if not mostrar:
        plt.close(fig)

    # 6. Estados: matrices discretas. Etiquetas de clasificación completas debajo.
    valores = ["Sin lluvia", "Baja posibilidad", "Lluvia probable", "Lluvia"]
    codigos = np.array([[valores.index(estado) for estado in orig["estado"]],
                        [valores.index(estado) for estado in ajust["estado"]]])
    from matplotlib.colors import ListedColormap, BoundaryNorm
    colores = ListedColormap(["#D4DDE5", "#F5D49A", "#91CDC1", "#4388B6"])
    norma = BoundaryNorm([-.5, .5, 1.5, 2.5, 3.5], colores.N)
    fig, ax = _crear(figsize=(11, 4.4))
    m = ax.imshow(codigos, cmap=colores, norm=norma, aspect="auto")
    ax.set_xticks(x, horas)
    ax.set_yticks([0, 1], ["Original", "Ajustado"])
    ax.set_xlabel("Hora de medición")
    ax.set_title("06 | Estados asignados por cada escenario", fontsize=15, weight="bold", loc="left", pad=16)
    for fila in range(2):
        for col in range(len(horas)):
            ax.text(col, fila, f"{[orig, ajust][fila]['indice'][col]:.3f}",
                    ha="center", va="center", color="#15293B", fontsize=10, weight="bold")
    ax.grid(False)
    barra = fig.colorbar(m, ax=ax, shrink=.75, pad=.02, ticks=range(4))
    barra.ax.set_yticklabels(valores)
    fig.savefig(salida / "06_estados_por_hora.png", dpi=175)
    rutas.append(salida / "06_estados_por_hora.png")
    if not mostrar:
        plt.close(fig)

    if mostrar:
        plt.show()
        plt.close("all")
    return rutas
