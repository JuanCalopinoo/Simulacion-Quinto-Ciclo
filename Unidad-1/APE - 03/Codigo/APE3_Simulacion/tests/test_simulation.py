"""Pruebas de la simulación M/M/1 y del controlador de la aplicación.

Las pruebas no exigen que la simulación coincida exactamente con la teoría:
comprueban coherencia, reproducibilidad, validación de parámetros y
correcto funcionamiento de los tres escenarios obligatorios.
"""

import math
import unittest
from pathlib import Path

from controller import simulation_controller as controller
from model.queue_model import run_simulation

LAMBDA_RATE = 2.0
MU_RATE = 3.0
NUM_CUSTOMERS = 300
SEED = 1234


class TestSimulationModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_simulation(LAMBDA_RATE, MU_RATE, NUM_CUSTOMERS, SEED)

    def test_requested_number_of_customers_is_generated(self):
        self.assertEqual(len(self.result.customers), NUM_CUSTOMERS)
        self.assertEqual(self.result.num_customers, NUM_CUSTOMERS)

    def test_all_customers_are_served(self):
        identifiers = [record.customer_id for record in self.result.customers]

        self.assertEqual(identifiers, list(range(1, NUM_CUSTOMERS + 1)))
        for record in self.result.customers:
            self.assertTrue(math.isfinite(record.departure_time))
            self.assertGreaterEqual(record.departure_time, record.service_start)

    def test_waiting_and_system_times_are_coherent(self):
        for record in self.result.customers:
            self.assertGreaterEqual(record.waiting_time, 0.0)
            self.assertGreaterEqual(record.service_duration, 0.0)
            self.assertAlmostEqual(
                record.system_time,
                record.waiting_time + record.service_duration,
                places=6,
            )
            self.assertGreaterEqual(record.service_start, record.arrival_time)

    def test_server_capacity_is_one(self):
        """El servidor nunca atiende a dos clientes al mismo tiempo."""

        ordered = sorted(
            self.result.customers, key=lambda record: record.service_start
        )
        for previous, current in zip(ordered, ordered[1:]):
            self.assertGreaterEqual(
                current.service_start,
                previous.departure_time - 1e-9,
                "Se detectaron dos atenciones simultáneas.",
            )

    def test_results_have_no_impossible_values(self):
        simulation = self.result

        self.assertTrue(math.isfinite(simulation.avg_waiting_time))
        self.assertTrue(math.isfinite(simulation.avg_system_time))
        self.assertTrue(math.isfinite(simulation.avg_queue_length))
        self.assertTrue(math.isfinite(simulation.utilization))

        self.assertGreaterEqual(simulation.avg_waiting_time, 0.0)
        self.assertGreaterEqual(simulation.avg_system_time, 0.0)
        self.assertGreaterEqual(simulation.avg_queue_length, 0.0)
        self.assertGreaterEqual(simulation.utilization, 0.0)
        self.assertLessEqual(simulation.utilization, 1.0)
        self.assertGreater(simulation.observation_time, 0.0)

    def test_same_configuration_and_seed_is_reproducible(self):
        first = run_simulation(LAMBDA_RATE, MU_RATE, 150, 77)
        second = run_simulation(LAMBDA_RATE, MU_RATE, 150, 77)

        self.assertEqual(first.avg_waiting_time, second.avg_waiting_time)
        self.assertEqual(first.avg_queue_length, second.avg_queue_length)
        self.assertEqual(first.utilization, second.utilization)
        self.assertEqual(
            [record.arrival_time for record in first.customers],
            [record.arrival_time for record in second.customers],
        )
        self.assertEqual(
            [record.departure_time for record in first.customers],
            [record.departure_time for record in second.customers],
        )

    def test_invalid_parameters_are_rejected(self):
        invalid_cases = [
            {"lambda_rate": 2.0, "mu_rate": 3.0, "num_customers": 0, "seed": 1},
            {"lambda_rate": 2.0, "mu_rate": 3.0, "num_customers": -5, "seed": 1},
            {"lambda_rate": 2.0, "mu_rate": 3.0, "num_customers": 10.5, "seed": 1},
            {"lambda_rate": 0.0, "mu_rate": 3.0, "num_customers": 10, "seed": 1},
            {"lambda_rate": -1.0, "mu_rate": 3.0, "num_customers": 10, "seed": 1},
            {"lambda_rate": 2.0, "mu_rate": 0.0, "num_customers": 10, "seed": 1},
            {"lambda_rate": 2.0, "mu_rate": -3.0, "num_customers": 10, "seed": 1},
            {"lambda_rate": 2.0, "mu_rate": 3.0, "num_customers": 10, "seed": -1},
            {"lambda_rate": 2.0, "mu_rate": 3.0, "num_customers": 10, "seed": 1.5},
        ]

        for case in invalid_cases:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    run_simulation(**case)


class TestController(unittest.TestCase):
    def test_predefined_scenarios_run_correctly(self):
        results = controller.run_all_scenarios(num_customers=200, seed=7)
        expected_lambdas = [2.0, 2.5, 2.9]

        self.assertEqual(len(results), 3)
        for result, expected_lambda in zip(results, expected_lambdas):
            with self.subTest(lambda_rate=expected_lambda):
                simulation = result["simulation"]
                self.assertEqual(result["scenario"]["lambda_rate"], expected_lambda)
                self.assertEqual(simulation.num_customers, 200)
                self.assertEqual(len(simulation.customers), 200)
                self.assertTrue(math.isfinite(simulation.avg_waiting_time))
                self.assertTrue(math.isfinite(simulation.avg_queue_length))
                self.assertLess(simulation.utilization, 1.0)

    def test_single_scenario_result_structure(self):
        result = controller.run_scenario("1", 100, 42)

        self.assertIn("scenario", result)
        self.assertIn("theoretical", result)
        self.assertIn("simulation", result)
        self.assertEqual(result["scenario"]["id"], "1")
        self.assertEqual(result["simulation"].seed, 42)
        self.assertEqual(len(result["simulation"].customers), 100)

    def test_comparison_rows_contain_required_columns(self):
        results = controller.run_all_scenarios(150, 7)
        rows = controller.build_comparison_rows(results)

        required_columns = {
            "Escenario",
            "λ",
            "μ",
            "ρ teórica",
            "L teórica",
            "Lq teórica",
            "Wq teórica (t. espera)",
            "Wq simulada (t. espera)",
            "Lq simulada (cola)",
        }

        self.assertEqual(len(rows), 3)
        for row in rows:
            self.assertTrue(required_columns.issubset(row.keys()))

    def test_controller_rejects_invalid_inputs(self):
        invalid_inputs = [(0, 1), (-3, 1), (100, -1), (10.5, 1), (100, 1.5)]

        for num_customers, seed in invalid_inputs:
            with self.subTest(num_customers=num_customers, seed=seed):
                with self.assertRaises(ValueError):
                    controller.run_scenario("1", num_customers, seed)

    def test_unknown_scenario_is_rejected(self):
        with self.assertRaises(ValueError):
            controller.get_scenario("99")


class TestArchitecture(unittest.TestCase):
    def test_model_and_controller_do_not_import_streamlit(self):
        """La separación MVC obliga a que el modelo y el controlador no
        dependan de la interfaz."""

        root = Path(__file__).resolve().parents[1]
        sources = [
            root / "model" / "queue_model.py",
            root / "model" / "metrics.py",
            root / "controller" / "simulation_controller.py",
        ]

        for source_path in sources:
            with self.subTest(file=source_path.name):
                content = source_path.read_text(encoding="utf-8").lower()
                self.assertNotIn("import streamlit", content)


if __name__ == "__main__":
    unittest.main()
