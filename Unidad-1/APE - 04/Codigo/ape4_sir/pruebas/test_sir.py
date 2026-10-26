"""Pruebas automaticas: ejecutarlas con python3 -m unittest discover -s pruebas -v."""
import csv
from pathlib import Path
from random import Random
from unittest.mock import patch
import tempfile
import unittest

from config import ParametrosSIR
from modelo.poblacion import Estado, contar_estados, crear_poblacion
from modelo.transiciones import avanzar_paso
from resultados.exportador import COLUMNAS_NETLOGO, exportar_csv
from simulacion.motor import ejecutar


class TestPoblacion(unittest.TestCase):
    def test_condicion_inicial(self):
        agentes = crear_poblacion(100, 5, Random(42))
        self.assertEqual(contar_estados(agentes), (95, 5, 0))

    def test_parametros_invalidos(self):
        with self.assertRaises(ValueError):
            ParametrosSIR(beta=1.2)
        with self.assertRaises(ValueError):
            ParametrosSIR(infectados_iniciales=101)
        with self.assertRaises(ValueError):
            ParametrosSIR(contactos_por_infectado=100)

    def test_enteros_sin_booleanos(self):
        for nombre in ("poblacion", "infectados_iniciales", "pasos",
                       "contactos_por_infectado", "semilla"):
            for valor in (1.5, True, "5", None):
                with self.subTest(nombre=nombre, valor=valor):
                    with self.assertRaises(ValueError):
                        ParametrosSIR(**{nombre: valor})

    def test_rangos_invalidos(self):
        for valores in ({"poblacion": 1}, {"infectados_iniciales": -1},
                        {"pasos": -1}, {"contactos_por_infectado": 0},
                        {"beta": float("nan")}, {"gamma": -0.1}):
            with self.subTest(valores=valores):
                with self.assertRaises(ValueError):
                    ParametrosSIR(**valores)


class TestTransiciones(unittest.TestCase):
    def test_sin_contagios_y_recuperacion_total(self):
        inicial = [Estado.INFECTADO, Estado.INFECTADO, Estado.SUSCEPTIBLE]
        siguiente, eventos = avanzar_paso(inicial, 0, 1, Random(7))
        self.assertEqual(contar_estados(siguiente), (1, 0, 2))
        self.assertEqual(eventos.nuevos_contagios, 0)
        self.assertEqual(eventos.nuevas_recuperaciones, 2)

    def test_sin_transiciones(self):
        inicial = [Estado.INFECTADO, Estado.SUSCEPTIBLE]
        siguiente, eventos = avanzar_paso(inicial, 0, 0, Random(8))
        self.assertEqual(inicial, siguiente)
        self.assertEqual(eventos.nuevos_contagios, 0)

    def test_recien_infectado_no_se_recupera_mismo_paso(self):
        inicial = [Estado.INFECTADO, Estado.SUSCEPTIBLE]
        siguiente, eventos = avanzar_paso(inicial, 1, 1, Random(8))
        self.assertEqual(siguiente, [Estado.RECUPERADO, Estado.INFECTADO])
        self.assertEqual(eventos.nuevos_contagios, 1)
        self.assertEqual(eventos.nuevas_recuperaciones, 1)

    def test_contagio_duplicado_y_copia_del_estado(self):
        inicial = [Estado.INFECTADO, Estado.INFECTADO, Estado.SUSCEPTIBLE]
        siguiente, eventos = avanzar_paso(inicial, 1, 0, Random(1), 2)
        self.assertEqual(inicial, [Estado.INFECTADO, Estado.INFECTADO, Estado.SUSCEPTIBLE])
        self.assertEqual(contar_estados(siguiente), (0, 3, 0))
        self.assertEqual(eventos.nuevos_contagios, 1)

    def test_recien_infectado_no_contagia_mismo_paso(self):
        inicial = [Estado.INFECTADO, Estado.SUSCEPTIBLE, Estado.SUSCEPTIBLE]
        siguiente, eventos = avanzar_paso(inicial, 1, 0, Random(1))
        self.assertEqual(eventos.nuevos_contagios, 1)
        self.assertEqual(contar_estados(siguiente), (1, 2, 0))


class TestMotor(unittest.TestCase):
    def test_101_registros_y_conservacion(self):
        p = ParametrosSIR()
        resultado = ejecutar(p)
        self.assertEqual(len(resultado.registros), 101)
        self.assertEqual(resultado.registros[0].tiempo, 0)
        self.assertEqual(resultado.registros[-1].tiempo, 100)
        self.assertEqual(resultado.registros[0].susceptibles, 95)
        self.assertEqual([r.tiempo for r in resultado.registros], list(range(101)))
        for registro in resultado.registros:
            self.assertEqual(registro.susceptibles + registro.infectados + registro.recuperados, 100)
            self.assertGreaterEqual(min(registro.susceptibles, registro.infectados, registro.recuperados), 0)
        resultado.validar()

    def test_semilla_reproducible(self):
        p = ParametrosSIR(semilla=1337)
        a = ejecutar(p)
        b = ejecutar(p)
        self.assertEqual(a.registros, b.registros)

    def test_csv_formato_netlogo(self):
        r = ejecutar(ParametrosSIR(pasos=3))
        with tempfile.TemporaryDirectory() as temp:
            ruta = exportar_csv(r, Path(temp) / "resultados_python.csv")
            with ruta.open(newline="", encoding="utf-8") as f:
                filas = list(csv.reader(f))
        self.assertEqual(filas[0], COLUMNAS_NETLOGO)
        self.assertEqual(len(filas), 5)  # 1 encabezado + t=0..3
        self.assertEqual(filas[1], ["0", "95", "5", "0"])
        self.assertEqual([[int(v) for v in fila] for fila in filas[1:]],
                         [[x.tiempo, x.susceptibles, x.infectados, x.recuperados]
                          for x in r.registros])

    def test_extincion_sin_contagios(self):
        p = ParametrosSIR(beta=0, gamma=1, pasos=5)
        r = ejecutar(p)
        self.assertEqual(r.registros[1].infectados, 0)
        self.assertEqual(r.registros[-1].recuperados, 5)


    def test_sin_infectados_conserva_todos_los_tiempos(self):
        resultado = ejecutar(ParametrosSIR(infectados_iniciales=0))
        self.assertEqual(len(resultado.registros), 101)
        self.assertTrue(all((r.susceptibles, r.infectados, r.recuperados) == (100, 0, 0)
                            for r in resultado.registros))

    def test_cero_pasos(self):
        resultado = ejecutar(ParametrosSIR(pasos=0))
        self.assertEqual(len(resultado.registros), 1)
        self.assertEqual((resultado.registros[0].susceptibles,
                          resultado.registros[0].infectados,
                          resultado.registros[0].recuperados), (95, 5, 0))

    def test_ejecuciones_no_comparten_estado(self):
        parametros = ParametrosSIR()
        a = ejecutar(parametros)
        esperado = a.registros.copy()
        a.registros.clear()
        self.assertEqual(ejecutar(parametros).registros, esperado)

    def test_simpy_faltante_informa_error(self):
        with patch.dict("sys.modules", {"simpy": None}):
            with self.assertRaisesRegex(RuntimeError, "Falta SimPy"):
                ejecutar(ParametrosSIR())


if __name__ == "__main__":
    unittest.main()
