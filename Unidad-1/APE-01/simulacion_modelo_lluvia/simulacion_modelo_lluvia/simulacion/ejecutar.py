"""Lectura, validación y exportación de resultados numéricos."""

import csv
from collections import Counter
from pathlib import Path

import numpy as np

from modelo.lluvia import MODELO_AJUSTADO, MODELO_ORIGINAL, calcular_modelo


CAMPOS_ENTRADA = ("hora", "humedad", "nubosidad", "temperatura")


def cargar_mediciones(ruta):
    ruta = Path(ruta)
    with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames is None or any(c not in lector.fieldnames for c in CAMPOS_ENTRADA):
            raise ValueError(f"El CSV debe contener: {', '.join(CAMPOS_ENTRADA)}")
        filas = list(lector)
    if not filas:
        raise ValueError("El archivo CSV está vacío.")

    horas, minutos, humedad, nubosidad, temperatura = [], [], [], [], []
    for numero, fila in enumerate(filas, 2):
        try:
            hora = fila["hora"].strip()
            partes = hora.split(":")
            if len(partes) != 2 or len(partes[0]) != 2 or len(partes[1]) != 2:
                raise ValueError("hora inválida")
            hh, mm = int(partes[0]), int(partes[1])
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                raise ValueError("hora fuera del reloj")
            humedad.append(float(fila["humedad"]))
            nubosidad.append(float(fila["nubosidad"]))
            temperatura.append(float(fila["temperatura"]))
            horas.append(f"{hh:02d}:{mm:02d}")
            minutos.append(hh * 60 + mm)
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError(f"Datos inválidos en la fila {numero}: {fila}") from error
    if len(set(minutos)) != len(minutos):
        raise ValueError("Se encontraron horas duplicadas.")
    if minutos != sorted(minutos):
        raise ValueError("Las horas deben estar ordenadas ascendentemente.")

    datos = {
        "hora": horas,
        "humedad": np.asarray(humedad, dtype=float),
        "nubosidad": np.asarray(nubosidad, dtype=float),
        "temperatura": np.asarray(temperatura, dtype=float),
    }
    if not np.all(np.isfinite(datos["temperatura"])):
        raise ValueError("Temperaturas no finitas.")
    return datos


def ejecutar_simulacion(datos):
    return {
        "original": calcular_modelo(datos["humedad"], datos["nubosidad"],
                                    datos["temperatura"], MODELO_ORIGINAL),
        "ajustado": calcular_modelo(datos["humedad"], datos["nubosidad"],
                                    datos["temperatura"], MODELO_AJUSTADO),
    }


def escribir_tablas(datos, escenarios, directorio):
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    rutas = []
    for nombre, resultado in escenarios.items():
        ruta = directorio / f"tabla_{nombre}.csv"
        with ruta.open("w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["Hora", "Humedad (%)", "Nubosidad (%)", "Temperatura (°C)",
                               "H", "N", "Tf", "Índice", "Índice (%)", "Estado"])
            for j, hora in enumerate(datos["hora"]):
                escritor.writerow([
                    hora, f"{datos['humedad'][j]:.0f}", f"{datos['nubosidad'][j]:.0f}",
                    f"{datos['temperatura'][j]:.0f}", f"{resultado['H'][j]:.3f}",
                    f"{resultado['N'][j]:.3f}", f"{resultado['Tf'][j]:.3f}",
                    f"{resultado['indice'][j]:.4f}", f"{100 * resultado['indice'][j]:.2f}",
                    resultado["estado"][j],
                ])
        rutas.append(ruta)

    ruta = directorio / "comparacion_escenarios.csv"
    with ruta.open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["Hora", "Índice original", "Estado original", "Índice ajustado",
                           "Estado ajustado", "Diferencia ajustado-original"])
        o, a = escenarios["original"], escenarios["ajustado"]
        for j, hora in enumerate(datos["hora"]):
            escritor.writerow([hora, f"{o['indice'][j]:.4f}", o["estado"][j],
                               f"{a['indice'][j]:.4f}", a["estado"][j],
                               f"{a['indice'][j] - o['indice'][j]:+.4f}"])
    rutas.append(ruta)
    return rutas


def imprimir_resumen(datos, escenarios):
    print("\nSIMULACIÓN DE LLUVIA | Guía APE 001 | Mediciones disponibles: 06:00-22:00")
    print("Nota: el índice es una regla académica, no una probabilidad calibrada.\n")
    for clave, modelo in escenarios.items():
        print(f"ESCENARIO: {clave.upper()}")
        print(f"{'Hora':<7}{'H':>7}{'N':>7}{'Tf':>7}{'Índice':>10}   Estado")
        print("-" * 59)
        for j, hora in enumerate(datos["hora"]):
            print(f"{hora:<7}{modelo['H'][j]:>7.2f}{modelo['N'][j]:>7.2f}"
                  f"{modelo['Tf'][j]:>7.2f}{modelo['indice'][j]:>10.4f}   {modelo['estado'][j]}")
        resumen = Counter(modelo["estado"])
        print("Promedio del índice:", f"{np.mean(modelo['indice']):.4f}",
              "| Máximo:", f"{np.max(modelo['indice']):.4f}",
              "a las", datos["hora"][int(np.argmax(modelo["indice"]))])
        print("Estados:", ", ".join(f"{estado}: {resumen[estado]}" for estado in
                                    ["Sin lluvia", "Baja posibilidad", "Lluvia probable", "Lluvia"]))
        print()
