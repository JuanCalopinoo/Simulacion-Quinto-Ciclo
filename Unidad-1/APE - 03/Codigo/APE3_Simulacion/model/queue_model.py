"""Modelo de simulación de eventos discretos para una cola M/M/1.

Este módulo contiene únicamente la lógica del modelo:

* Se crea un entorno SimPy y un recurso de capacidad 1 (un solo servidor).
* Los clientes llegan según una distribución exponencial (proceso de Poisson).
* Cada cliente espera su turno bajo disciplina FIFO y luego es atendido.
* Los tiempos de servicio también siguen una distribución exponencial.
* Se integran en el tiempo la longitud de la cola y el estado del servidor
  para obtener promedios temporales reales.

El módulo no importa Streamlit. La función principal es ``run_simulation``.
"""

from dataclasses import dataclass

import numpy as np
import simpy


@dataclass
class CustomerRecord:
    """Datos registrados de cada cliente durante la simulación."""

    customer_id: int
    arrival_time: float
    service_start: float
    waiting_time: float
    service_duration: float
    departure_time: float
    system_time: float


@dataclass
class SimulationResult:
    """Resultado completo de una réplica de simulación."""

    lambda_rate: float
    mu_rate: float
    num_customers: int
    seed: int

    customers: list

    observation_time: float
    queue_area: float
    busy_area: float

    avg_waiting_time: float
    avg_system_time: float
    avg_queue_length: float
    utilization: float

    queue_series_times: list
    queue_series_lengths: list


class _TimeIntegral:
    """Área bajo una variable entera que solo cambia en eventos.

    Guarda el valor actual de una variable (por ejemplo, la cantidad de
    clientes esperando). Cada vez que la variable cambia se acumula el área
    del intervalo anterior. El promedio temporal es ``area / tiempo_total``.

    Si ``track_history`` es verdadero, guarda la lista de pares
    ``(instante, valor)`` para poder dibujar la evolución de la variable.
    """

    def __init__(self, track_history=False):
        self.area = 0.0
        self.value = 0
        self.last_time = 0.0
        self.history = [(0.0, 0)] if track_history else None

    def set_value(self, new_value, now):
        self.area += self.value * (now - self.last_time)
        self.value = new_value
        self.last_time = now
        if self.history is not None:
            self.history.append((now, new_value))


def _validate_parameters(lambda_rate, mu_rate, num_customers, seed):
    """Comprueba que los parámetros de entrada sean válidos."""

    if isinstance(lambda_rate, bool) or not isinstance(
        lambda_rate, (int, float, np.integer, np.floating)
    ):
        raise ValueError("La tasa de llegada λ debe ser un número.")
    if isinstance(mu_rate, bool) or not isinstance(
        mu_rate, (int, float, np.integer, np.floating)
    ):
        raise ValueError("La tasa de servicio μ debe ser un número.")
    if lambda_rate <= 0:
        raise ValueError("La tasa de llegada λ debe ser mayor que cero.")
    if mu_rate <= 0:
        raise ValueError("La tasa de servicio μ debe ser mayor que cero.")

    if isinstance(num_customers, bool) or not isinstance(
        num_customers, (int, np.integer)
    ):
        raise ValueError("La cantidad de clientes debe ser un número entero.")
    if num_customers < 1:
        raise ValueError("La cantidad de clientes debe ser al menos 1.")

    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)):
        raise ValueError("La semilla debe ser un número entero.")
    if seed < 0:
        raise ValueError("La semilla debe ser mayor o igual que cero.")


def _check_consistency(customers):
    """Comprueba que los tiempos registrados sean coherentes.

    Se verifica que ningún tiempo de espera sea negativo, que el tiempo total
    en el sistema sea la suma de la espera y el servicio, y que el servidor
    no atienda a dos clientes al mismo tiempo.
    """

    tolerance = 1e-6
    ordered = sorted(customers, key=lambda record: record.service_start)
    previous_departure = None

    for record in ordered:
        if record.waiting_time < -tolerance:
            raise RuntimeError(
                f"El cliente {record.customer_id} tiene un tiempo de espera negativo."
            )
        if abs(record.system_time - (record.waiting_time + record.service_duration)) > tolerance:
            raise RuntimeError(
                f"El tiempo en el sistema del cliente {record.customer_id} "
                "no coincide con la espera más el servicio."
            )
        if previous_departure is not None and record.service_start < previous_departure - tolerance:
            raise RuntimeError(
                "El servidor atendió a dos clientes al mismo tiempo: "
                "la capacidad debería ser 1."
            )
        previous_departure = record.departure_time


def _customer_process(env, server, rng, mu_rate, customer_id, records, queue_integral, busy_integral):
    """Proceso SimPy que representa la vida de un cliente."""

    arrival_time = env.now

    with server.request() as request:
        # Desde que pide el servidor hasta que lo obtiene, el cliente espera.
        # Si el servidor está libre esta espera dura cero unidades de tiempo.
        queue_integral.set_value(queue_integral.value + 1, env.now)
        yield request

        service_start = env.now
        queue_integral.set_value(queue_integral.value - 1, env.now)

        service_duration = rng.exponential(1.0 / mu_rate)
        busy_integral.set_value(busy_integral.value + 1, env.now)
        yield env.timeout(service_duration)
        busy_integral.set_value(busy_integral.value - 1, env.now)

    departure_time = env.now
    records.append(
        CustomerRecord(
            customer_id=customer_id,
            arrival_time=arrival_time,
            service_start=service_start,
            waiting_time=service_start - arrival_time,
            service_duration=service_duration,
            departure_time=departure_time,
            system_time=departure_time - arrival_time,
        )
    )


def _arrival_process(env, server, rng, lambda_rate, mu_rate, num_customers, records, queue_integral, busy_integral):
    """Genera los clientes respetando los tiempos entre llegadas."""

    for customer_id in range(1, num_customers + 1):
        interarrival_time = rng.exponential(1.0 / lambda_rate)
        yield env.timeout(interarrival_time)
        env.process(
            _customer_process(
                env,
                server,
                rng,
                mu_rate,
                customer_id,
                records,
                queue_integral,
                busy_integral,
            )
        )


def run_simulation(lambda_rate, mu_rate, num_customers, seed):
    """Ejecuta una réplica de la cola M/M/1 y devuelve los resultados.

    Se simulan exactamente ``num_customers`` clientes. La simulación avanza
    hasta que todos los clientes han terminado su servicio, por lo que todos
    los clientes generados quedan incluidos en las métricas.

    El intervalo de observación es ``[0, T]``, donde ``T`` es el instante en
    que el último cliente termina su servicio. Los promedios temporales de la
    longitud de la cola y de la utilización del servidor se calculan sobre
    ese intervalo.

    Args:
        lambda_rate: tasa media de llegada λ (clientes por unidad de tiempo).
        mu_rate: tasa media de servicio μ (clientes por unidad de tiempo).
        num_customers: cantidad de clientes a generar.
        seed: semilla del generador aleatorio para reproducir la ejecución.

    Returns:
        Un ``SimulationResult`` con los clientes atendidos y las métricas
        simuladas.
    """

    _validate_parameters(lambda_rate, mu_rate, num_customers, seed)

    env = simpy.Environment()
    server = simpy.Resource(env, capacity=1)
    rng = np.random.default_rng(seed)

    records = []
    queue_integral = _TimeIntegral(track_history=True)
    busy_integral = _TimeIntegral()

    env.process(
        _arrival_process(
            env,
            server,
            rng,
            lambda_rate,
            mu_rate,
            num_customers,
            records,
            queue_integral,
            busy_integral,
        )
    )
    env.run()

    if len(records) != num_customers:
        raise RuntimeError(
            "La simulación terminó antes de atender a todos los clientes."
        )

    _check_consistency(records)

    observation_time = env.now
    queue_integral.history.append((observation_time, queue_integral.value))

    waiting_times = np.array([record.waiting_time for record in records])
    system_times = np.array([record.system_time for record in records])

    avg_queue_length = queue_integral.area / observation_time
    utilization = busy_integral.area / observation_time

    return SimulationResult(
        lambda_rate=float(lambda_rate),
        mu_rate=float(mu_rate),
        num_customers=int(num_customers),
        seed=int(seed),
        customers=records,
        observation_time=observation_time,
        queue_area=queue_integral.area,
        busy_area=busy_integral.area,
        avg_waiting_time=float(waiting_times.mean()),
        avg_system_time=float(system_times.mean()),
        avg_queue_length=float(avg_queue_length),
        utilization=float(utilization),
        queue_series_times=[instant for instant, _ in queue_integral.history],
        queue_series_lengths=[length for _, length in queue_integral.history],
    )
