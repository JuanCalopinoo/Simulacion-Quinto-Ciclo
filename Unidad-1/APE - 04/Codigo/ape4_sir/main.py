#!/usr/bin/env python3
"""Entrada de la simulación SIR de la práctica APE 4."""
import argparse
from pathlib import Path
import sys
import time

from config import ParametrosSIR
from resultados.exportador import exportar_csv
from resultados.graficas import guardar_grafica
from simulacion.motor import ejecutar

RAIZ = Path(__file__).resolve().parent


def crear_argumentos() -> argparse.Namespace:
    valores = ParametrosSIR()
    parser = argparse.ArgumentParser(description="Modelo SIR por agentes con SimPy.")
    parser.add_argument("--poblacion", type=int, default=valores.poblacion)
    parser.add_argument("--infectados", type=int, default=valores.infectados_iniciales)
    parser.add_argument("--beta", type=float, default=valores.beta)
    parser.add_argument("--gamma", type=float, default=valores.gamma)
    parser.add_argument("--pasos", type=int, default=valores.pasos)
    parser.add_argument("--contactos", type=int, default=valores.contactos_por_infectado)
    parser.add_argument("--semilla", type=int, default=valores.semilla)
    parser.add_argument("--salida", type=Path, default=RAIZ / "datos",
                        help="Carpeta para resultados_python.csv; puede ser la del .nlogo.")
    parser.add_argument("--graficas", type=Path, default=RAIZ / "graficas",
                        help="Carpeta para sir_evolucion.png.")
    return parser.parse_args()


def main() -> int:
    args = crear_argumentos()
    try:
        parametros = ParametrosSIR(
            poblacion=args.poblacion, infectados_iniciales=args.infectados,
            beta=args.beta, gamma=args.gamma, pasos=args.pasos,
            contactos_por_infectado=args.contactos, semilla=args.semilla,
        )
        inicio = time.perf_counter()
        resultado = ejecutar(parametros)
        duracion = time.perf_counter() - inicio
        # Verificar las dependencias gráficas antes de exportar el CSV.
        ruta_grafica = guardar_grafica(resultado, args.graficas)
        ruta_csv = exportar_csv(resultado, args.salida / "resultados_python.csv")
        pico = max(resultado.registros, key=lambda r: r.infectados)
        final = resultado.registros[-1]
        print("MODELO SIR - Python + SimPy")
        print(f"Semilla: {parametros.semilla} | Registros: {len(resultado.registros)}")
        print(f"Pico de infectados: {pico.infectados} en t={pico.tiempo}")
        print(f"Final (S, I, R): {final.susceptibles}, {final.infectados}, {final.recuperados}")
        print(f"Tiempo de simulación computacional: {duracion:.4f} s")
        print(f"CSV para NetLogo: {ruta_csv}")
        print(f"Gráfica: {ruta_grafica}")
        return 0
    except ImportError as exc:
        print(f"ERROR: falta una dependencia ({exc}). "
              "Ejecute: python -m pip install -r requirements.txt", file=sys.stderr)
        return 1
    except (ValueError, RuntimeError, AssertionError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
