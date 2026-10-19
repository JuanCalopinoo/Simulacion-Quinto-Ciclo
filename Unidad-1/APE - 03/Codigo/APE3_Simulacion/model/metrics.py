"""Métricas teóricas del modelo M/M/1 y validación de tasas.

Las fórmulas se calculan en estado estacionario y solo tienen sentido cuando
el sistema es estable, es decir, cuando λ < μ.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TheoreticalMetrics:
    """Métricas teóricas de una cola M/M/1 en estado estacionario.

    * ``rho``: utilización del servidor, λ / μ.
    * ``L``: número promedio de clientes en el sistema.
    * ``Lq``: número promedio de clientes en la cola.
    * ``W``: tiempo promedio de permanencia en el sistema.
    * ``Wq``: tiempo promedio de espera en la cola.
    """

    rho: float
    L: float
    Lq: float
    W: float
    Wq: float


def validate_rates(lambda_rate, mu_rate):
    """Valida que las tasas sean positivas y que el sistema sea estable."""

    if lambda_rate <= 0:
        raise ValueError("La tasa de llegada λ debe ser mayor que cero.")
    if mu_rate <= 0:
        raise ValueError("La tasa de servicio μ debe ser mayor que cero.")
    if lambda_rate >= mu_rate:
        raise ValueError(
            "El sistema no es estable: se requiere λ < μ para calcular las "
            f"métricas estacionarias (λ = {lambda_rate}, μ = {mu_rate})."
        )


def theoretical_metrics(lambda_rate, mu_rate):
    """Calcula las métricas teóricas de una cola M/M/1.

    Fórmulas utilizadas:

    * rho = λ / μ
    * L   = λ / (μ - λ)
    * Lq  = λ² / (μ · (μ - λ))
    * W   = 1 / (μ - λ)
    * Wq  = λ / (μ · (μ - λ))
    """

    validate_rates(lambda_rate, mu_rate)

    rho = lambda_rate / mu_rate
    L = lambda_rate / (mu_rate - lambda_rate)
    Lq = lambda_rate ** 2 / (mu_rate * (mu_rate - lambda_rate))
    W = 1.0 / (mu_rate - lambda_rate)
    Wq = lambda_rate / (mu_rate * (mu_rate - lambda_rate))

    return TheoreticalMetrics(rho=rho, L=L, Lq=Lq, W=W, Wq=Wq)
