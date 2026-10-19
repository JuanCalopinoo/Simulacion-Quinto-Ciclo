"""Pruebas de las métricas teóricas del modelo M/M/1.

Se verifican valores exactos, la definición de la utilización y el rechazo de
parámetros inválidos o inestables.
"""

import unittest

from model.metrics import theoretical_metrics, validate_rates


class TestTheoreticalMetrics(unittest.TestCase):
    def test_metrics_for_lambda_2_mu_3(self):
        """Los valores teóricos de λ = 2.0 y μ = 3.0 son conocidos."""

        metrics = theoretical_metrics(2.0, 3.0)

        self.assertAlmostEqual(metrics.rho, 2.0 / 3.0)
        self.assertAlmostEqual(metrics.L, 2.0)
        self.assertAlmostEqual(metrics.Lq, 4.0 / 3.0)
        self.assertAlmostEqual(metrics.W, 1.0)
        self.assertAlmostEqual(metrics.Wq, 2.0 / 3.0)

    def test_utilization_is_lambda_over_mu(self):
        """La utilización debe calcularse como λ/μ y no como μ/λ."""

        metrics = theoretical_metrics(2.9, 3.0)

        self.assertAlmostEqual(metrics.rho, 2.9 / 3.0)
        self.assertNotAlmostEqual(metrics.rho, 3.0 / 2.9)

    def test_relationships_between_metrics(self):
        """Se cumplen las relaciones de Little y L = Lq + ρ."""

        lambda_rate, mu_rate = 2.0, 3.0
        metrics = theoretical_metrics(lambda_rate, mu_rate)

        self.assertAlmostEqual(metrics.L, lambda_rate * metrics.W)
        self.assertAlmostEqual(metrics.Lq, lambda_rate * metrics.Wq)
        self.assertAlmostEqual(metrics.L, metrics.Lq + metrics.rho)

    def test_stability_condition_is_enforced(self):
        """El sistema no es estable cuando λ >= μ."""

        unstable = [(3.0, 3.0), (4.0, 3.0), (2.9, 2.5), (10.0, 10.0)]

        for lambda_rate, mu_rate in unstable:
            with self.subTest(lambda_rate=lambda_rate, mu_rate=mu_rate):
                with self.assertRaises(ValueError):
                    theoretical_metrics(lambda_rate, mu_rate)

    def test_non_positive_rates_are_rejected(self):
        """Las tasas deben ser positivas."""

        invalid = [(0.0, 3.0), (-1.0, 3.0), (2.0, 0.0), (2.0, -3.0)]

        for lambda_rate, mu_rate in invalid:
            with self.subTest(lambda_rate=lambda_rate, mu_rate=mu_rate):
                with self.assertRaises(ValueError):
                    theoretical_metrics(lambda_rate, mu_rate)

    def test_predefined_scenarios_are_valid(self):
        """Los tres escenarios obligatorios son estables."""

        for lambda_rate in (2.0, 2.5, 2.9):
            with self.subTest(lambda_rate=lambda_rate):
                metrics = theoretical_metrics(lambda_rate, 3.0)
                self.assertLess(metrics.rho, 1.0)
                self.assertGreater(metrics.Wq, 0.0)

    def test_validate_rates_allows_stable_system(self):
        """No debe lanzar error cuando λ < μ y ambas son positivas."""

        validate_rates(2.0, 3.0)


if __name__ == "__main__":
    unittest.main()
