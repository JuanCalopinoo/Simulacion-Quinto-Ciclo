"""Autora: Katheryn Contento. Exportacion CSV para NetLogo."""
import csv
from pathlib import Path

from simulacion.motor import ResultadoSIR


COLUMNAS_NETLOGO = ["tiempo", "susceptibles", "infectados", "recuperados"]


def exportar_csv(resultado: ResultadoSIR, destino: Path) -> Path:
    """CSV compatible con NetLogo: 4 columnas exactas, sin indice adicional."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(COLUMNAS_NETLOGO)
        for r in resultado.registros:
            escritor.writerow([r.tiempo, r.susceptibles, r.infectados, r.recuperados])
    return destino

