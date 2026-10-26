#!/usr/bin/env python3
"""Ejecutar con python3 main.py: calcula, grafica y crea el PDF resuelto."""

import argparse
from pathlib import Path
import sys

# En Linux sin interfaz gráfica, generar imágenes/PDF no exige DISPLAY.
if "--mostrar" not in sys.argv:
    import matplotlib
    matplotlib.use("Agg")

from simulacion.ejecutar import (cargar_mediciones, ejecutar_simulacion,
                                 escribir_tablas, imprimir_resumen)
from graficas.generar import generar_graficas
from reportes.crear_pdf import generar_informe, generar_markdown


def main():
    raiz = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="APE 001: índice académico de lluvia, tablas, seis gráficas e informe PDF"
    )
    parser.add_argument("--datos", type=Path, default=raiz / "datos" / "mediciones.csv",
                        help="CSV con hora, humedad, nubosidad y temperatura")
    parser.add_argument("--mostrar", action="store_true",
                        help="Además de guardar, abrir gráficas en ventanas (Linux con entorno gráfico)")
    args = parser.parse_args()
    try:
        datos = cargar_mediciones(args.datos)
        escenarios = ejecutar_simulacion(datos)
        tablas = escribir_tablas(datos, escenarios, raiz / "resultados")
        graficas = generar_graficas(datos, escenarios, raiz / "graficas", mostrar=args.mostrar)
        informe = generar_informe(datos, escenarios, graficas, raiz / "resultados" / "practica_01_resuelta.pdf")
        editable = generar_markdown(datos, escenarios, raiz / "docs" / "practica_resuelta_editable.md")
        imprimir_resumen(datos, escenarios)
        print("ARCHIVOS GENERADOS:")
        for ruta in [*tablas, *graficas, informe, editable]:
            print(f"  {ruta.relative_to(raiz)}")
        print("\nEjecución correcta.")
    except (OSError, ValueError) as error:
        parser.exit(1, f"ERROR: {error}\n")


if __name__ == "__main__":
    main()
