"""Punto de entrada de la aplicación Streamlit: Simulación M/M/1.

El archivo se limita a conectar la vista con el controlador: dibuja la
interfaz, ejecuta la simulación cuando el usuario lo solicita y presenta los
resultados. Toda la lógica del modelo y de coordinación vive en las carpetas
``model/`` y ``controller/``.
"""

import streamlit as st

from controller import simulation_controller as controller
from view import dashboard

st.set_page_config(page_title="Simulación M/M/1", layout="wide")

dashboard.render_header()

config = dashboard.render_config_panel()

if config["run"]:
    try:
        if config["compare"]:
            results = controller.run_all_scenarios(
                config["num_customers"], config["seed"]
            )
        else:
            results = [
                controller.run_scenario(
                    config["scenario_id"],
                    config["num_customers"],
                    config["seed"],
                )
            ]
        st.session_state["results"] = results
        st.session_state["run_config"] = {
            "num_customers": config["num_customers"],
            "seed": config["seed"],
        }
    except ValueError as error:
        st.error(f"Parámetros no válidos: {error}")
    except Exception as error:
        st.exception(error)

if "results" in st.session_state:
    run_config = st.session_state["run_config"]
    dashboard.render_results(
        st.session_state["results"],
        run_config["num_customers"],
        run_config["seed"],
    )
else:
    st.info(
        "Configure los parámetros en el panel lateral y pulse "
        "**Iniciar simulación** para obtener resultados."
    )

dashboard.render_educational_section()
