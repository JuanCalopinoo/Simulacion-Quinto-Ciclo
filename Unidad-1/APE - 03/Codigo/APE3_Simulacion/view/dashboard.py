"""Vista de la aplicación M/M/1.

Contiene los componentes de presentación: encabezado, controles, tarjetas de
resultados, tablas comparativas, gráficas y la explicación educativa. Solo
esta capa utiliza Streamlit y Matplotlib.
"""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import streamlit as st

from controller import simulation_controller as controller

SCENARIO_COLORS = {"1": "#2563eb", "2": "#f59e0b", "3": "#dc2626"}

COMPARE_OPTION = "all"
COMPARE_LABEL = "Comparar los tres escenarios"

MAX_TABLE_ROWS = 200
DECIMALS = 3


def _scenario_label(scenario):
    return (
        f"{scenario['nombre']} (λ={scenario['lambda_rate']}, "
        f"μ={scenario['mu_rate']}) · {scenario['descripcion']}"
    )


def render_header():
    """Dibuja el encabezado académico de la aplicación."""

    st.title("Simulación de un sistema de líneas de espera M/M/1")
    st.markdown(
        "**Asignatura:** Simulación · **Carrera:** Computación · "
        "**Universidad Nacional de Loja**"
    )
    st.markdown(
        "La aplicación simula una cola M/M/1 con SimPy, calcula las métricas "
        "teóricas del modelo y las compara con los valores obtenidos por la "
        "simulación, incluyendo la evolución de la cola y los tiempos de espera."
    )
    st.divider()


def render_config_panel():
    """Dibuja el panel de configuración y devuelve la selección del usuario."""

    st.sidebar.header("Panel de configuración")

    scenario_options = {
        _scenario_label(scenario): scenario["id"]
        for scenario in controller.get_scenarios()
    }
    scenario_options[COMPARE_LABEL] = COMPARE_OPTION

    selected_label = st.sidebar.selectbox(
        "Escenario a ejecutar",
        options=list(scenario_options.keys()),
        help=(
            "Los tres escenarios obligatorios de la práctica, o la opción para "
            "ejecutar los tres y compararlos entre sí."
        ),
    )
    selected_option = scenario_options[selected_label]

    num_customers = st.sidebar.number_input(
        "Cantidad de clientes",
        min_value=1,
        max_value=100000,
        value=1000,
        step=100,
        help=(
            "Clientes que se generan en cada ejecución. A mayor cantidad, más "
            "próximos suelen ser los resultados a la teoría y más tardía es la "
            "simulación."
        ),
    )
    seed = st.sidebar.number_input(
        "Semilla aleatoria",
        min_value=0,
        max_value=2 ** 31 - 1,
        value=42,
        step=1,
        help=(
            "Semilla del generador aleatorio. Con la misma semilla y la misma "
            "configuración se reproducen exactamente los mismos resultados."
        ),
    )

    run_clicked = st.sidebar.button(
        "Iniciar simulación", type="primary", width="stretch"
    )

    return {
        "scenario_id": selected_option,
        "compare": selected_option == COMPARE_OPTION,
        "num_customers": int(num_customers),
        "seed": int(seed),
        "run": run_clicked,
    }


def render_main_metrics(result):
    """Muestra las tarjetas con los indicadores principales de un escenario."""

    theoretical = result["theoretical"]
    simulation = result["simulation"]

    columns = st.columns(4)
    with columns[0]:
        st.metric("Utilización teórica (ρ)", f"{theoretical.rho:.{DECIMALS}f}")
    with columns[1]:
        st.metric(
            "Wq simulada (espera promedio)",
            f"{simulation.avg_waiting_time:.{DECIMALS}f}",
        )
    with columns[2]:
        st.metric(
            "Lq simulada (cola promedio)",
            f"{simulation.avg_queue_length:.{DECIMALS}f}",
        )
    with columns[3]:
        st.metric("Clientes atendidos", simulation.num_customers)

    scenario = result["scenario"]
    st.caption(
        f"{scenario['nombre']}: λ = {scenario['lambda_rate']}, "
        f"μ = {scenario['mu_rate']}, semilla = {simulation.seed}, "
        f"intervalo de observación [0, {simulation.observation_time:.{DECIMALS}f}]."
    )


def render_comparison_table(rows):
    """Presenta la tabla comparativa entre teoría y simulación."""

    st.subheader("Comparación de resultados teóricos y simulados")
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption(
        "Las columnas cuyo nombre termina en 'teórica' provienen de las "
        "fórmulas del modelo M/M/1; el resto proviene de la simulación. Los "
        "valores simulados no coinciden exactamente con los teóricos debido a "
        "la variabilidad aleatoria, al tamaño de la muestra y a las condiciones "
        "de observación."
    )


def _plot_queue_evolution(scenario, theoretical, simulation):
    color = SCENARIO_COLORS.get(scenario["id"], "#2563eb")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.step(
        simulation.queue_series_times,
        simulation.queue_series_lengths,
        where="post",
        color=color,
        linewidth=1.2,
        label="Tamaño de la cola (simulado)",
    )
    ax.axhline(
        theoretical.Lq,
        color="#111827",
        linestyle="--",
        linewidth=1.5,
        label=f"Lq teórica = {theoretical.Lq:.{DECIMALS}f}",
    )
    ax.set_title(f"{scenario['nombre']}: evolución del tamaño de la cola")
    ax.set_xlabel("Tiempo (unidades de tiempo)")
    ax.set_ylabel("Clientes esperando (clientes)")
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def _plot_waiting_histogram(scenario, theoretical, simulation):
    waiting_times = [record.waiting_time for record in simulation.customers]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(
        waiting_times,
        bins=30,
        color=SCENARIO_COLORS.get(scenario["id"], "#2563eb"),
        edgecolor="white",
    )
    ax.axvline(
        theoretical.Wq,
        color="#111827",
        linestyle="--",
        linewidth=1.5,
        label=f"Wq teórica = {theoretical.Wq:.{DECIMALS}f}",
    )
    ax.axvline(
        simulation.avg_waiting_time,
        color="#b91c1c",
        linestyle="-",
        linewidth=1.5,
        label=f"Wq simulada = {simulation.avg_waiting_time:.{DECIMALS}f}",
    )
    ax.set_title(f"{scenario['nombre']}: distribución de los tiempos de espera")
    ax.set_xlabel("Tiempo de espera en la cola (unidades de tiempo)")
    ax.set_ylabel("Cantidad de clientes")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def _plot_comparison_bars(rows, theoretical_key, simulated_key, title, ylabel):
    labels = [row["Escenario"] for row in rows]
    theoretical_values = [row[theoretical_key] for row in rows]
    simulated_values = [row[simulated_key] for row in rows]

    positions = list(range(len(labels)))
    width = 0.38

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(
        [position - width / 2 for position in positions],
        theoretical_values,
        width,
        label="Teórica",
        color="#94a3b8",
    )
    ax.bar(
        [position + width / 2 for position in positions],
        simulated_values,
        width,
        label="Simulada",
        color="#2563eb",
    )
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def _show_figure(fig):
    st.pyplot(fig)
    plt.close(fig)


def render_charts(result):
    """Muestra la evolución de la cola y la distribución de esperas."""

    _show_figure(
        _plot_queue_evolution(
            result["scenario"], result["theoretical"], result["simulation"]
        )
    )
    _show_figure(
        _plot_waiting_histogram(
            result["scenario"], result["theoretical"], result["simulation"]
        )
    )


def render_comparison_charts(rows):
    """Muestra las gráficas comparativas entre los tres escenarios."""

    _show_figure(
        _plot_comparison_bars(
            rows,
            theoretical_key="Wq teórica (t. espera)",
            simulated_key="Wq simulada (t. espera)",
            title="Tiempo promedio de espera en la cola (Wq)",
            ylabel="Tiempo de espera (unidades de tiempo)",
        )
    )
    _show_figure(
        _plot_comparison_bars(
            rows,
            theoretical_key="Lq teórica",
            simulated_key="Lq simulada (cola)",
            title="Tamaño promedio de la cola (Lq)",
            ylabel="Clientes esperando (clientes)",
        )
    )


def render_customers_table(simulation):
    """Presenta los datos individuales de los clientes en una tabla limitada."""

    records = simulation.customers
    visible = records[:MAX_TABLE_ROWS]

    rows = [
        {
            "Cliente": record.customer_id,
            "Llegada": round(record.arrival_time, DECIMALS),
            "Inicio servicio": round(record.service_start, DECIMALS),
            "Espera (Wq)": round(record.waiting_time, DECIMALS),
            "Servicio": round(record.service_duration, DECIMALS),
            "Salida": round(record.departure_time, DECIMALS),
            "En sistema (W)": round(record.system_time, DECIMALS),
        }
        for record in visible
    ]
    st.dataframe(rows, width="stretch", hide_index=True)

    if len(records) > MAX_TABLE_ROWS:
        st.caption(
            f"Se muestran los primeros {MAX_TABLE_ROWS} de {len(records)} "
            "clientes para no saturar la interfaz."
        )


def render_results(results, num_customers, seed):
    """Presenta todos los resultados obtenidos por el controlador."""

    rows = controller.build_comparison_rows(results)
    compare_mode = len(results) > 1

    st.caption(
        f"Configuración utilizada: {num_customers} clientes, semilla {seed} "
        "(la misma semilla se aplica a cada escenario)."
    )
    render_comparison_table(rows)

    if compare_mode:
        st.subheader("Comparación entre escenarios")
        render_comparison_charts(rows)

        for result in results:
            scenario = result["scenario"]
            with st.expander(
                f"Detalle de {scenario['nombre']} "
                f"(λ={scenario['lambda_rate']}, μ={scenario['mu_rate']})"
            ):
                render_main_metrics(result)
                render_charts(result)
                render_customers_table(result["simulation"])
    else:
        st.subheader("Resultados principales")
        render_main_metrics(results[0])
        st.subheader("Visualización")
        render_charts(results[0])
        with st.expander("Datos de clientes"):
            render_customers_table(results[0]["simulation"])


def render_educational_section():
    """Explicación breve para comprender y defender el modelo en clase."""

    st.divider()
    st.subheader("Explicación educativa")
    st.markdown(
        """
**¿Qué es el modelo M/M/1?** Es una cola con llegadas aleatorias (primera M),
tiempos de servicio aleatorios (segunda M) y un único servidor (1) que atiende
por orden de llegada, es decir, con disciplina FIFO.

**λ (lambda)** es la tasa media de llegada de clientes y **μ (mu)** la tasa
media de servicio del servidor; ambas se expresan en clientes por unidad de
tiempo. **ρ = λ / μ** es la utilización teórica del servidor: la proporción de
tiempo en que el servidor está ocupado. Para que el sistema sea estable se
requiere λ < μ, es decir, ρ < 1.

**L frente a Lq:** L es el número promedio de clientes en todo el sistema
(esperando más el que está siendo atendido); Lq es solamente el número
promedio de clientes esperando en la cola.

**W frente a Wq:** W es el tiempo promedio que un cliente pasa en el sistema
(espera más servicio); Wq es solamente el tiempo promedio de espera en la
cola.

**¿Por qué aumenta la espera cuando λ se acerca a μ?** El servidor dispone de
cada vez menos tiempo libre para absorber las llegadas, de modo que más
clientes encuentran el servidor ocupado, la cola crece y los tiempos de espera
se incrementan de forma acelerada. Si λ fuera mayor o igual que μ el sistema
sería inestable y la cola crecería sin límite.
        """
    )
