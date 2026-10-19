"""Controlador de la aplicación M/M/1.

El controlador:

* Define los escenarios obligatorios de la práctica.
* Valida los parámetros que envía la interfaz.
* Ejecuta la simulación del modelo y el cálculo de métricas teóricas.
* Prepara las filas de la tabla comparativa para la vista.

No contiene código de dibujo de la interfaz.
"""

from model import metrics
from model.queue_model import run_simulation

SCENARIOS = [
    {
        "id": "1",
        "nombre": "Escenario 1",
        "descripcion": "Sistema estable",
        "lambda_rate": 2.0,
        "mu_rate": 3.0,
    },
    {
        "id": "2",
        "nombre": "Escenario 2",
        "descripcion": "Mayor utilización",
        "lambda_rate": 2.5,
        "mu_rate": 3.0,
    },
    {
        "id": "3",
        "nombre": "Escenario 3",
        "descripcion": "Cerca de la saturación",
        "lambda_rate": 2.9,
        "mu_rate": 3.0,
    },
]

ALL_SCENARIOS_ID = "all"


def get_scenarios():
    """Devuelve la lista de escenarios obligatorios."""

    return list(SCENARIOS)


def get_scenario(scenario_id):
    """Busca un escenario por su identificador."""

    for scenario in SCENARIOS:
        if scenario["id"] == scenario_id:
            return scenario
    raise ValueError(f"El escenario '{scenario_id}' no existe.")


def validate_inputs(num_customers, seed):
    """Valida la cantidad de clientes y la semilla antes de simular."""

    if isinstance(num_customers, bool) or not isinstance(num_customers, int):
        raise ValueError("La cantidad de clientes debe ser un número entero.")
    if num_customers < 1:
        raise ValueError("La cantidad de clientes debe ser al menos 1.")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("La semilla debe ser un número entero.")
    if seed < 0:
        raise ValueError("La semilla debe ser mayor o igual que cero.")


def run_scenario(scenario_id, num_customers, seed):
    """Ejecuta un escenario completo: métricas teóricas más simulación.

    Returns:
        Diccionario con las claves ``scenario``, ``theoretical`` y
        ``simulation``.
    """

    validate_inputs(num_customers, seed)
    scenario = get_scenario(scenario_id)

    theoretical = metrics.theoretical_metrics(
        scenario["lambda_rate"], scenario["mu_rate"]
    )
    simulation = run_simulation(
        scenario["lambda_rate"],
        scenario["mu_rate"],
        num_customers,
        seed,
    )

    return {
        "scenario": scenario,
        "theoretical": theoretical,
        "simulation": simulation,
    }


def run_all_scenarios(num_customers, seed):
    """Ejecuta los tres escenarios con la misma configuración y semilla."""

    return [
        run_scenario(scenario["id"], num_customers, seed)
        for scenario in SCENARIOS
    ]


def build_comparison_rows(results):
    """Convierte los resultados en filas listas para la tabla comparativa.

    Las columnas cuyo nombre termina en "teórica" provienen de las fórmulas
    del modelo; el resto proviene de la simulación.
    """

    rows = []
    for result in results:
        scenario = result["scenario"]
        theoretical = result["theoretical"]
        simulation = result["simulation"]

        rows.append(
            {
                "Escenario": scenario["nombre"],
                "λ": scenario["lambda_rate"],
                "μ": scenario["mu_rate"],
                "ρ teórica": round(theoretical.rho, 4),
                "L teórica": round(theoretical.L, 4),
                "Lq teórica": round(theoretical.Lq, 4),
                "W teórica (t. sistema)": round(theoretical.W, 4),
                "Wq teórica (t. espera)": round(theoretical.Wq, 4),
                "Wq simulada (t. espera)": round(simulation.avg_waiting_time, 4),
                "Lq simulada (cola)": round(simulation.avg_queue_length, 4),
                "W simulada (t. sistema)": round(simulation.avg_system_time, 4),
                "Utilización simulada": round(simulation.utilization, 4),
            }
        )
    return rows
