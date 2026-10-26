"""Informe resuelto en PDF con Matplotlib (sin dependencias adicionales)."""

from collections import Counter
from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

AZUL = "#173A56"
TURQUESA = "#137B92"
GRIS = "#4C5968"
NARANJA = "#C87827"


def _pagina(titulo, subtitulo, numero):
    fig = plt.figure(figsize=(11.69, 8.27), facecolor="white")
    fig.text(.065, .944, "UNIVERSIDAD NACIONAL DE LOJA  /  SIMULACIÓN  /  APE 001",
             fontsize=9.5, color=TURQUESA, weight="bold")
    fig.text(.065, .889, titulo, fontsize=21, color=AZUL, weight="bold")
    fig.text(.065, .852, subtitulo, fontsize=10.4, color=GRIS)
    fig.add_artist(plt.Line2D([.065, .937], [.827, .827], transform=fig.transFigure,
                              color=TURQUESA, lw=1.5))
    fig.text(.065, .041, "Fuente de datos: Guía APE 001 (2026), págs. 2–4. Elaboración académica a partir de la guía.",
             fontsize=8.3, color=GRIS)
    fig.text(.937, .041, f"{numero}", ha="right", fontsize=8.3, color=GRIS)
    return fig


def _texto(fig, x, y, texto, ancho=148, tam=10.8, interlineado=1.55, color=GRIS):
    # Ajustar el ancho del párrafo a los márgenes reales de la página A4.
    # Así no se corta texto a la derecha, incluso en el panel lateral.
    ancho_seguro = max(22, int((.935 - x) * 841.7 / (tam * .53)))
    envuelto = textwrap.fill(texto, width=min(ancho, ancho_seguro),
                             break_long_words=False, break_on_hyphens=False)
    fig.text(x, y, envuelto, fontsize=tam, va="top", color=color, linespacing=interlineado)
    return y - (len(envuelto.splitlines()) * tam * interlineado / 600)


def _tabla(fig, datos, columnas, posicion, anchos=None, tam=10):
    ax = fig.add_axes(posicion)
    ax.axis("off")
    if anchos is None:
        anchos = [1 / len(columnas)] * len(columnas)
    tabla = ax.table(cellText=datos, colLabels=columnas, loc="center",
                     cellLoc="center", colLoc="center", bbox=[0, 0, 1, 1], colWidths=anchos)
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(tam)
    for (fila, columna), celda in tabla.get_celld().items():
        celda.set_linewidth(.25)
        celda.set_edgecolor("#CBD5DD")
        if fila == 0:
            celda.set_facecolor(AZUL)
            celda.set_text_props(color="white", weight="bold")
        else:
            celda.set_facecolor("#EAF2F5" if fila % 2 else "white")
            celda.set_text_props(color="#263E50")
    return tabla


def _filas(datos, modelo):
    return [
        [hora, f"{datos['humedad'][j]:.0f}", f"{datos['nubosidad'][j]:.0f}",
         f"{datos['temperatura'][j]:.0f}", f"{modelo['H'][j]:.2f}",
         f"{modelo['N'][j]:.2f}", f"{modelo['Tf'][j]:.2f}",
         f"{modelo['indice'][j]:.3f}", str(modelo["estado"][j])]
        for j, hora in enumerate(datos["hora"])
    ]


def _resumen(modelo, horas):
    estados = Counter(modelo["estado"])
    return (f"Índice promedio: {np.mean(modelo['indice']):.4f}. "
            f"Máximo: {np.max(modelo['indice']):.4f} ({horas[int(np.argmax(modelo['indice']))]}). "
            f"Mínimo: {np.min(modelo['indice']):.4f} ({horas[int(np.argmin(modelo['indice']))]}). "
            f"Baja posibilidad: {estados['Baja posibilidad']} horarios; "
            f"lluvia probable: {estados['Lluvia probable']}; "
            f"lluvia: {estados['Lluvia']}; sin lluvia: {estados['Sin lluvia']}.")


def generar_informe(datos, escenarios, graficas, ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    o, a = escenarios["original"], escenarios["ajustado"]
    columnas = ["Hora", "Humedad\n(%)", "Nubosidad\n(%)", "Temp.\n(°C)",
                "H", "N", "Tf", "Índice I", "Clasificación"]
    anchuras = [.10, .115, .115, .095, .07, .07, .07, .095, .27]
    with PdfPages(ruta, metadata={"Title": "Práctica 01 resuelta - Modelo matemático de lluvia",
                                 "Author": "Proyecto académico Python"}) as pdf:
        # Portada sustantiva (no únicamente decorativa)
        fig = _pagina("Construcción y simulación de un modelo matemático",
                      "Práctica N.º 01 · Unidad 1 · Carrera de Computación · Ciclo 5 · 2026", 1)
        fig.text(.07, .766, "1. Objetivo", fontsize=14, color=AZUL, weight="bold")
        _texto(fig, .07, .738, "Implementar el índice I = 0.5H + 0.3N + 0.2Tf, determinar los estados de lluvia para los horarios proporcionados y analizar gráficamente el efecto de modificar sus parámetros.")
        fig.text(.07, .666, "2. Datos originales (sin inventar nuevas observaciones)",
                 fontsize=14, color=AZUL, weight="bold")
        entradas = [[datos['hora'][j], f"{datos['humedad'][j]:.0f} %",
                     f"{datos['nubosidad'][j]:.0f} %", f"{datos['temperatura'][j]:.0f} °C"]
                    for j in range(len(datos['hora']))]
        _tabla(fig, entradas, ["Hora", "Humedad", "Nubosidad", "Temperatura"],
               [.07, .265, .59, .35], tam=10.1)
        fig.text(.70, .618, "3. Reglas de clasificación", fontsize=13.5, color=AZUL, weight="bold")
        reglas = [["I < 0.40", "Sin lluvia"], ["0.40 ≤ I < 0.60", "Baja posibilidad"],
                  ["0.60 ≤ I < 0.75", "Lluvia probable"], ["I ≥ 0.75", "Lluvia"]]
        _tabla(fig, reglas, ["Índice", "Estado"], [.70, .397, .23, .19], tam=9)
        fig.text(.70, .349, "4. Transformaciones", fontsize=13.5, color=AZUL, weight="bold")
        _texto(fig, .70, .322, "H = humedad / 100; N = nubosidad / 100. Tf se obtiene de la tabla del enunciado; para 15 y 17 °C se interpola linealmente entre valores vecinos.",
               ancho=48, tam=9.4, interlineado=1.5)
        fig.text(.07, .190, "Alcance:", fontsize=11.5, color=AZUL, weight="bold")
        _texto(fig, .145, .190, "La guía plantea 24 horas, pero solo entrega nueve lecturas de 06:00 a 22:00. Se modelan exclusivamente esas nueve horas. Las etiquetas describen una regla matemática, no una predicción meteorológica validada.",
               ancho=122, tam=10)
        pdf.savefig(fig)
        plt.close(fig)

        # Solución del índice inicial
        fig = _pagina("Tabla 1 · Modelo original", "I = 0.50H + 0.30N + 0.20Tf", 2)
        _tabla(fig, _filas(datos, o), columnas, [.065, .26, .87, .52], anchuras, tam=9.55)
        fig.text(.071, .732, "Cálculo por fila: I = 0.50 × H + 0.30 × N + 0.20 × Tf",
                 fontsize=12.5, color=AZUL)
        fig.text(.07, .230, "Interpretación de la tabla", fontsize=13.3, color=AZUL, weight="bold")
        _texto(fig, .07, .195, _resumen(o, datos["hora"]), ancho=146, tam=10.4)
        pdf.savefig(fig)
        plt.close(fig)

        # Modelo ajustado; identificación de hipótesis del alumno
        fig = _pagina("Tabla 2 · Modelo ajustado", "I = 0.60H + 0.30N + 0.10Tf · Escenario propuesto para la comparación", 3)
        _tabla(fig, _filas(datos, a), columnas, [.065, .26, .87, .52], anchuras, tam=9.55)
        fig.text(.07, .231, "Interpretación del ajuste", fontsize=13.3, color=AZUL, weight="bold")
        _texto(fig, .07, .196, _resumen(a, datos["hora"]) +
               " Se aumenta el peso de humedad en 0.10 y se disminuye el factor de temperatura en 0.10, manteniendo la suma de pesos en 1.",
               ancho=148, tam=10.25)
        pdf.savefig(fig)
        plt.close(fig)

        # Tabla de comparación de diferencias
        fig = _pagina("Tabla 3 · Comparación de escenarios", "Cambios por horario y análisis de crecimiento o decrecimiento", 4)
        comparacion = []
        for j, hora in enumerate(datos["hora"]):
            comparacion.append([hora, f"{o['indice'][j]:.3f}", str(o['estado'][j]),
                                f"{a['indice'][j]:.3f}", str(a['estado'][j]),
                                f"{a['indice'][j]-o['indice'][j]:+.3f}"])
        _tabla(fig, comparacion,
               ["Hora", "I original", "Estado original", "I ajustado", "Estado ajustado", "Diferencia"],
               [.065, .326, .87, .41], [.10, .13, .245, .13, .245, .15], tam=9.25)
        fig.text(.07, .279, "Análisis", fontsize=13.2, color=AZUL, weight="bold")
        cambios = [datos['hora'][j] for j in range(len(datos['hora'])) if o['estado'][j] != a['estado'][j]]
        texto = ("Las categorías cambian a las " + ", ".join(cambios) + ". " if cambios else "No cambian categorías. ")
        diferencias = np.diff(o["indice"])
        suben = [f"{datos['hora'][j]}–{datos['hora'][j+1]}" for j in range(len(diferencias)) if diferencias[j] > 0]
        bajan = [f"{datos['hora'][j]}–{datos['hora'][j+1]}" for j in range(len(diferencias)) if diferencias[j] < 0]
        texto += "El índice original crece en los intervalos " + ", ".join(suben) + "; decrece en " + ", ".join(bajan) + "."
        _texto(fig, .07, .246, texto, ancho=150, tam=10.1)
        pdf.savefig(fig)
        plt.close(fig)

        # Control y conclusiones. 'r' y P0 no pertenecen a la fórmula de lluvia.
        fig = _pagina("Preguntas de control y conclusiones", "Respuestas a los cinco puntos de la página 4 de la guía", 5)
        preguntas = [
            ("1. ¿Qué es un modelo matemático?",
             "Es una representación simplificada de un sistema mediante variables, parámetros y ecuaciones; permite analizar cómo cambian los resultados al variar entradas o supuestos."),
            ("2. ¿Cuál es la diferencia entre variable y parámetro?",
             "Una variable puede cambiar entre observaciones, como la humedad, la nubosidad y la temperatura. Un parámetro define el comportamiento de la fórmula; aquí son 0.5, 0.3 y 0.2 en el modelo original."),
            ("3. ¿Qué representa P₀?",
             "En el modelo exponencial P(t) = P₀·e^(rt), P₀ es el valor inicial en t = 0. La fórmula de lluvia de esta práctica no incluye P₀."),
            ("4. ¿Qué ocurre cuando r < 0?",
             "En P(t) = P₀·e^(rt), r negativo produce decrecimiento exponencial conforme transcurre el tiempo; r no aparece en el modelo de lluvia aquí usado."),
            ("5. ¿Qué limitaciones tiene el modelo exponencial?",
             "Supone una tasa proporcional constante, no representa límites de capacidad, cambios de tasa ni perturbaciones del entorno; por ello su validez puede reducirse a intervalos concretos."),
        ]
        y = .788
        for pregunta, respuesta in preguntas:
            fig.text(.075, y, pregunta, fontsize=11.2, weight="bold", color=AZUL)
            y = _texto(fig, .082, y-.023, respuesta, ancho=140, tam=9.8, interlineado=1.45)-.035
        fig.text(.075, .146, "Conclusión", fontsize=12.4, weight="bold", color=TURQUESA)
        _texto(fig, .075, .122, "La humedad y la nubosidad elevan el índice cuando aumentan. Bajo la regla de temperatura elegida, un valor de temperatura menor aporta un Tf mayor. El ajuste cambia la importancia relativa de estas variables, pero no prueba una mejora predictiva. Las preguntas sobre P₀ y r pertenecen a otro modelo mencionado en la guía.",
               ancho=150, tam=9.5, interlineado=1.35)
        pdf.savefig(fig)
        plt.close(fig)

        titulos = [
            ("Figura 1 · Variables de entrada", "Humedad, nubosidad y temperatura según las nueve mediciones originales."),
            ("Figura 2 · Factores normalizados", "H, N y Tf representados en la misma escala de 0 a 1."),
            ("Figura 3 · Evolución del índice", "Bandas correspondientes a las cuatro categorías de la guía."),
            ("Figura 4 · Influencia de las variables", "Aporte ponderado de humedad, nubosidad y temperatura al índice original."),
            ("Figura 5 · Efecto del ajuste", "Comparación de los índices original y ajustado, sin atribuir precisión predictiva."),
            ("Figura 6 · Clasificaciones finales", "Mapa de categorías por hora: los números son índices, no lluvias observadas."),
        ]
        for idx, (ruta_grafica, (titulo, nota)) in enumerate(zip(graficas, titulos), 6):
            fig = _pagina(titulo, nota, idx)
            ax = fig.add_axes([.075, .13, .86, .66])
            ax.imshow(plt.imread(ruta_grafica))
            ax.axis("off")
            pdf.savefig(fig)
            plt.close(fig)
    return ruta


def generar_markdown(datos, escenarios, ruta):
    """Documento editable con resultados resueltos y preguntas de la guía."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    o, a = escenarios["original"], escenarios["ajustado"]
    lineas = [
        "# Práctica N.º 01 resuelta — Simulación de un modelo matemático",
        "", "**Asignatura:** Simulación — Ciclo 5 — Universidad Nacional de Loja",
        "", "**Objetivo:** implementar y analizar el índice académico de lluvia de la guía APE 001.",
        "", "## Metodología", "",
        "- Modelo original: `I = 0.5H + 0.3N + 0.2Tf`.",
        "- Humedad normalizada: `H = humedad / 100`.",
        "- Nubosidad normalizada: `N = nubosidad / 100`.",
        "- Factor `Tf`: tabla de la guía; interpolación lineal para 15 °C y 17 °C.",
        "- Clasificaciones: I < 0.40 sin lluvia; 0.40 ≤ I < 0.60 baja posibilidad; 0.60 ≤ I < 0.75 lluvia probable; I ≥ 0.75 lluvia.",
        "- Ajuste para comparar parámetros: `I = 0.6H + 0.3N + 0.1Tf`.",
        "", "**Nota:** el PDF de la guía menciona 24 horas, pero proporciona solo nueve registros entre 06:00 y 22:00. No se agregan mediciones inexistentes.",
    ]
    for nombre, modelo in [("original", o), ("ajustado", a)]:
        lineas += ["", f"## Tabla — modelo {nombre}", "",
                   "| Hora | Humedad (%) | Nubosidad (%) | Temp. (°C) | H | N | Tf | Índice | Estado |",
                   "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
        for j, hora in enumerate(datos["hora"]):
            lineas.append(
                f"| {hora} | {datos['humedad'][j]:.0f} | {datos['nubosidad'][j]:.0f} | "
                f"{datos['temperatura'][j]:.0f} | {modelo['H'][j]:.2f} | {modelo['N'][j]:.2f} | "
                f"{modelo['Tf'][j]:.2f} | {modelo['indice'][j]:.3f} | {modelo['estado'][j]} |"
            )
        lineas += ["", _resumen(modelo, datos["hora"])]
    lineas += ["", "## Diferencias del ajuste", "",
               "| Hora | I original | Estado original | I ajustado | Estado ajustado | Δ índice |",
               "|---|---:|---|---:|---|---:|"]
    for j, hora in enumerate(datos["hora"]):
        lineas.append(f"| {hora} | {o['indice'][j]:.3f} | {o['estado'][j]} | {a['indice'][j]:.3f} | {a['estado'][j]} | {a['indice'][j]-o['indice'][j]:+.3f} |")
    lineas += ["", "## Preguntas de control", "",
               "**1. ¿Qué es un modelo matemático?** Es una representación simplificada de un sistema mediante ecuaciones, variables y parámetros.",
               "", "**2. ¿Diferencia entre variable y parámetro?** La variable toma valores que cambian (H, N, temperatura); el parámetro establece una característica fija del modelo (los pesos 0.5, 0.3 y 0.2).",
               "", "**3. ¿Qué es P₀?** En un modelo exponencial `P(t) = P₀ exp(rt)`, es el valor inicial cuando t = 0; no aparece en la fórmula de lluvia.",
               "", "**4. ¿Qué ocurre cuando r < 0?** En un modelo exponencial, la cantidad disminuye con el tiempo. El parámetro r no interviene en la ecuación de lluvia.",
               "", "**5. Limitaciones del modelo exponencial:** supone una tasa constante de cambio proporcional y no contempla saturación, recursos limitados o cambios externos.",
               "", "## Conclusiones", "",
               "Los índices más altos se observan hacia la tarde en estas nueve mediciones. Aumentar el peso de H y reducir el de Tf altera los índices y algunas categorías. El índice clasifica los datos de acuerdo con las reglas de la actividad: no equivale a una probabilidad real de precipitación ni a un pronóstico validado.",
               "", "## Gráficas generadas", "",
               "1. Variables atmosféricas (`graficas/01_variables_atmosfericas.png`).",
               "2. Factores normalizados (`graficas/02_factores_normalizados.png`).",
               "3. Índice y umbrales (`graficas/03_indice_y_umbrales.png`).",
               "4. Contribuciones ponderadas (`graficas/04_aportes_del_modelo.png`).",
               "5. Comparación (`graficas/05_comparacion_escenarios.png`).",
               "6. Categorías (`graficas/06_estados_por_hora.png`).",
               "", "**Fuente:** Guía de Actividades Práctico-Experimentales N.º 001, asignatura Simulación, UNL, 2026 (páginas 2 a 4).",
               ""]
    ruta.write_text("\n".join(lineas), encoding="utf-8")
    return ruta
