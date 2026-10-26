"""Pruebas automáticas con unittest, sin instalar librerías extra."""

import unittest
from pathlib import Path
import numpy as np

from modelo.lluvia import (MODELO_AJUSTADO, MODELO_ORIGINAL,
                           ConfiguracionModelo, factor_temperatura,
                           calcular_modelo, clasificar_indice)
from simulacion.ejecutar import cargar_mediciones, ejecutar_simulacion


RAIZ = Path(__file__).resolve().parents[1]


class PruebasModeloLluvia(unittest.TestCase):
    def test_ejemplo_81_por_ciento_de_la_guia(self):
        r = calcular_modelo([90], [80], [18])
        self.assertAlmostEqual(r["indice"][0], .81, places=9)
        self.assertEqual(r["estado"][0], "Lluvia")

    def test_temperaturas_de_tabla_y_extremos(self):
        t = factor_temperatura([-5, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 40])
        np.testing.assert_allclose(t, [1, 1, .9, .8, .7, .6, .5, .4, .3, .2, .1, .1])

    def test_interpolacion_para_valores_no_tabularizados(self):
        np.testing.assert_allclose(factor_temperatura([15, 17]), [.75, .65])

    def test_limites_categorias(self):
        categorias = clasificar_indice([0, .399999, .4, .599999, .6, .749999, .75, 1])
        self.assertEqual(list(categorias), [
            "Sin lluvia", "Sin lluvia", "Baja posibilidad", "Baja posibilidad",
            "Lluvia probable", "Lluvia probable", "Lluvia", "Lluvia"
        ])

    def test_valores_de_la_guia_en_los_nueve_horarios(self):
        datos = cargar_mediciones(RAIZ / "datos" / "mediciones.csv")
        r = ejecutar_simulacion(datos)
        self.assertEqual(len(datos["hora"]), 9)
        np.testing.assert_allclose(
            r["original"]["indice"], [.605, .64, .595, .47, .685, .8, .885, .84, .775], atol=1e-12)
        np.testing.assert_allclose(
            r["ajustado"]["indice"], [.59, .64, .603, .49, .71, .825, .907, .863, .78], atol=1e-12)

    def test_pesos_invalidos(self):
        with self.assertRaises(ValueError):
            ConfiguracionModelo("incorrecto", .5, .5, .5)

    def test_porcentajes_invalidos(self):
        with self.assertRaises(ValueError):
            calcular_modelo([110], [25], [18], MODELO_ORIGINAL)

    def test_pesos_ajustados_suman_uno(self):
        self.assertAlmostEqual(MODELO_AJUSTADO.peso_humedad +
                               MODELO_AJUSTADO.peso_nubosidad +
                               MODELO_AJUSTADO.peso_temperatura, 1.0)


if __name__ == "__main__":
    unittest.main()
