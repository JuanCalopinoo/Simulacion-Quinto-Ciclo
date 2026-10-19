# Simulación de un sistema de líneas de espera M/M/1

Práctica 03 de la asignatura **Simulación** — Carrera de **Computación** — **Universidad Nacional de Loja**.

Aplicación en Python que simula una cola M/M/1 con **SimPy**, calcula las métricas
teóricas del modelo, las compara con las métricas obtenidas por la simulación y
visualiza el comportamiento de la cola y los tiempos de espera mediante una
interfaz web local en **Streamlit**.

Aquí tienes una versión redactada en Markdown, lista para incluir en el `README.md` del proyecto:

Escritura

## Detalles de autoría
- Grupo: Nro. 2

### Integrantes

- KATHERYN MELISSA CONTENTO MALDONADO
- JUAN ALBERTO CALOPINO MARTINEZ
- WILSON PATRICIO PALMA SAMANIEGO
- BRYAN GUSTAVO TROYA VELEZ

### Información académica

- **Curso:** Computación - 5to "A"
- **Asignatura:** Simulación
- **Docente:** José O. Guamán Q.
- **Fecha de entrega:** 2026-10-18

---

## 1. Descripción del problema y propósito de la simulación

Los sistemas de líneas de espera (bancos, cajeros, ventanillas de atención,
servidores de red, etc.) reciben clientes de forma aleatoria y los atienden con
un tiempo de servicio también aleatorio. Cuando el ritmo de llegadas se acerca a
la capacidad de atención, la cola crece y los tiempos de espera aumentan de forma
acelerada.

El modelo **M/M/1** es el modelo más sencillo que representa esta situación:
llegadas de Poisson, tiempos de servicio exponenciales y un único servidor que
atiende por orden de llegada (FIFO). Su solución analítica es conocida, lo que lo
convierte en un excelente punto de partida para **comprobar** que una simulación
de eventos discretos reproduce el comportamiento descrito por la teoría.

El propósito de esta práctica es construir la simulación, medir experimentalmente
el desempeño del sistema y contrastar los resultados simulados con los valores
teóricos.

## 2. Objetivo general

Desarrollar una aplicación modular en Python que simule un sistema de líneas de
espera M/M/1 mediante SimPy, calcule sus métricas teóricas y simuladas, las
presente de forma comparativa y permita visualizar la evolución de la cola y la
distribución de los tiempos de espera a través de una interfaz web local.

## 3. Tecnologías utilizadas

| Tecnología | Uso dentro del proyecto |
|---|---|
| Python | Lenguaje de programación del proyecto |
| SimPy | Motor de simulación de eventos discretos (reloj, llegadas, recurso servidor) |
| NumPy | Generación de variables aleatorias exponenciales y cálculos estadísticos |
| Matplotlib | Construcción de las gráficas (evolución de la cola, histogramas, comparaciones) |
| Streamlit | Interfaz gráfica web local en español |
| unittest | Pruebas automatizadas (de la biblioteca estándar de Python) |

## 4. Descripción del modelo M/M/1

* **Primera M**: los tiempos entre llegadas siguen una distribución exponencial
  (equivalentes a un proceso de llegadas de Poisson).
* **Segunda M**: los tiempos de servicio siguen una distribución exponencial.
* **1**: existe un único servidor.
* **Disciplina FIFO**: primero en llegar, primero en ser atendido.
* Los tiempos entre llegadas y de servicio se expresan en la misma unidad de
  tiempo (por ejemplo, minutos).

Cada cliente se representa con: identificador, instante de llegada, inicio del
servicio, tiempo de espera, duración del servicio, instante de salida y tiempo
total en el sistema.

## 5. Parámetros y escenarios disponibles

| Parámetro | Significado |
|---|---|
| `lambda_rate` (λ) | Tasa media de llegada de clientes (clientes por unidad de tiempo) |
| `mu_rate` (μ) | Tasa media de servicio (clientes por unidad de tiempo) |
| `num_customers` | Cantidad de clientes generados en cada ejecución |
| `seed` | Semilla del generador aleatorio, para reproducir los resultados |

Escenarios obligatorios definidos en la guía de la práctica:

| Escenario | λ | μ | Característica | ρ = λ/μ |
|---|---:|---:|---|---:|
| 1 | 2.0 | 3.0 | Sistema estable | 0.667 |
| 2 | 2.5 | 3.0 | Mayor utilización | 0.833 |
| 3 | 2.9 | 3.0 | Cerca de la saturación | 0.967 |

La interfaz permite ejecutar **un escenario individual** o **los tres escenarios**
en una misma operación para compararlos. La cantidad de clientes y la semilla se
pueden modificar desde el panel de configuración sin alterar los valores de λ y μ
de los escenarios obligatorios.

## 6. Fórmulas de las métricas teóricas

Las métricas teóricas se calculan en `model/metrics.py`, en estado estacionario y
solo cuando el sistema es estable (λ < μ):

| Métrica | Fórmula |
|---|---|
| Utilización del servidor | `ρ = λ / μ` |
| Clientes promedio en el sistema | `L = λ / (μ − λ)` |
| Clientes promedio en la cola | `Lq = λ² / (μ · (μ − λ))` |
| Tiempo promedio en el sistema | `W = 1 / (μ − λ)` |
| Tiempo promedio en la cola | `Wq = λ / (μ · (μ − λ))` |
| Condición de estabilidad | `λ < μ` |

Si las tasas no son positivas o si λ ≥ μ, el programa **no** calcula las métricas
estacionarias y muestra un mensaje comprensible en español.

## 7. Arquitectura MVC y responsabilidades de los archivos

El proyecto aplica una arquitectura **MVC** sencilla, sin capas ni patrones
adicionales:

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Punto de entrada. Conecta la vista con el controlador; no contiene lógica del modelo |
| `model/queue_model.py` | Modelo de simulación: crea el entorno SimPy, el recurso de capacidad 1, genera clientes y registra sus tiempos |
| `model/metrics.py` | Métricas teóricas y validación de tasas (no depende de la interfaz) |
| `controller/simulation_controller.py` | Coordina: define los escenarios, valida parámetros, ejecuta el modelo y prepara la tabla comparativa |
| `view/dashboard.py` | Vista: encabezado, panel de configuración, tarjetas, tablas y gráficas con Streamlit y Matplotlib |
| `tests/test_metrics.py` | Pruebas de las métricas teóricas y de la validación de tasas |
| `tests/test_simulation.py` | Pruebas de la simulación, del controlador y de la separación MVC |

El **modelo** no importa Streamlit: puede ejecutarse sin interfaz gráfica. El
**controlador** no dibuja nada, solo coordina. La **vista** no simula, solo
presenta. Esta separación se comprueba en `tests/test_simulation.py`
(clase `TestArchitecture`).

### Decisiones de simulación documentadas

* **Cantidad fija de clientes**: cada ejecución genera exactamente
  `num_customers` clientes y la simulación avanza hasta que **todos** terminan su
  servicio. Por eso ninguna métrica excluye arbitrariamente a clientes que aún
  esperaban en la cola.
* **Intervalo de observación**: los promedios temporales se calculan en el
  intervalo `[0, T]`, donde `T` es el instante en que el último cliente termina su
  servicio.
* **Tamaño promedio de la cola (Lq)**: se integra el número de clientes esperando
  a lo largo del tiempo y se divide el área acumulada entre `T`. Se actualiza con
  eventos reales del modelo (cada vez que un cliente empieza a esperar o empieza a
  ser atendido), no con muestreos periódicos.
* **Utilización experimental**: se integra el tiempo en que el servidor estuvo
  ocupado y se divide entre `T`.
* **Aleatoriedad reproducible**: cada ejecución usa su propio generador
  `numpy.random.default_rng(seed)`. Al comparar los tres escenarios se utiliza la
  misma semilla y la misma cantidad de clientes para todos.
* **L y Lq no son lo mismo**: `L` incluye al cliente que está siendo atendido;
  `Lq` cuenta únicamente a quienes esperan en la cola.

## 8. Árbol real de carpetas

```
simulacion_mm1/                 <- raíz del repositorio (el nombre local puede variar)
├── app.py                      <- punto de entrada de Streamlit
├── model/
│   ├── __init__.py
│   ├── queue_model.py          <- simulación de eventos discretos con SimPy
│   └── metrics.py              <- métricas teóricas y validación de tasas
├── controller/
│   ├── __init__.py
│   └── simulation_controller.py<- escenarios, validación y tabla comparativa
├── view/
│   ├── __init__.py
│   └── dashboard.py            <- encabezado, controles, tablas y gráficas
├── tests/
│   ├── __init__.py
│   ├── test_metrics.py         <- pruebas de las métricas teóricas
│   └── test_simulation.py      <- pruebas de la simulación y del controlador
├── requirements.txt            <- dependencias directas con versiones verificadas
├── .gitignore                  <- excluye entornos virtuales, cachés y temporales
└── README.md                   <- este documento
```

## 9. Requisitos previos

* Python **3.12 o superior** (el proyecto fue verificado con Python 3.12 y 3.14).
* `pip` actualizado.
* Conexión a internet **solo** para instalar las dependencias. Una vez instaladas,
  la aplicación funciona sin conexión.

Comprobar la versión instalada:

```bash
python --version
```

En Windows puede usarse el lanzador `py` (por ejemplo `py -3.12 -m venv .venv`).

## 10. Instalación paso a paso

1. Obtener el proyecto (cuando el grupo cree el repositorio, sería `git clone <url>`).
2. Entrar en la carpeta del proyecto:

```bash
cd simulacion_mm1
```

3. Crear el entorno virtual:

### Linux / macOS

```bash
python3 -m venv .venv
```

### Windows (PowerShell)

```powershell
python -m venv .venv
```

### Windows (símbolo del sistema / CMD)

```bat
python -m venv .venv
```

Si en el equipo hay varias versiones de Python instaladas, conviene elegir
explícitamente una que sea 3.12 o superior, por ejemplo
`py -3.12 -m venv .venv`.

> **Importante:** un entorno virtual no se puede “cambiar de versión de Python”
> en el mismo directorio. Si el `.venv` ya existía y se vuelve a ejecutar
> `venv` sobre él, el intérprete se reemplaza pero las dependencias antiguas
> permanecen y aparecen errores como
> `ModuleNotFoundError: No module named 'numpy._core._multiarray_umath'`.
> En ese caso hay que **eliminar la carpeta `.venv`** y crearla otra vez desde cero.

## 11. Activación del entorno virtual

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows (PowerShell)

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows (símbolo del sistema / CMD)

```bat
.venv\Scripts\activate.bat
```

Cuando el entorno está activo, la terminal muestra `(.venv)` al comienzo de la
línea. Para salir del entorno se ejecuta `deactivate`.

## 12. Instalación de dependencias

Con el entorno virtual activado:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

La carpeta del entorno virtual (`.venv/`) **no** se sube al repositorio: ya está
excluida en `.gitignore`.

### Contenido de `requirements.txt`

```
simpy==4.1.2
numpy==2.5.4
matplotlib==3.11.2
streamlit==1.66.0
```

Son las cuatro dependencias directas del proyecto, con versiones que se
instalaron y probaron en un entorno virtual limpio (Python 3.12 y Python 3.14).

## 13. Ejecución de las pruebas

Las pruebas usan la biblioteca estándar `unittest`, por lo que no requieren
instalar nada adicional. Desde la **raíz del proyecto**, con el entorno virtual
activado:

```bash
python -m unittest -v
```

También se pueden ejecutar con descubrimiento explícito:

```bash
python -m unittest discover -s tests -t . -v
```

Resultado esperado: **20 pruebas ejecutadas, todas correctas (`OK`)**. Las pruebas
comprueban, entre otras cosas, que las métricas teóricas de λ = 2.0 y μ = 3.0 son
exactas, que la utilización se calcula como λ/μ, que se rechaza un sistema
inestable (λ ≥ μ), que se genera la cantidad de clientes solicitada, que todos son
atendidos, que los tiempos son coherentes, que el servidor no atiende a dos
clientes a la vez, que la misma semilla reproduce los resultados y que los tres
escenarios obligatorios se ejecutan correctamente.

## 14. Inicio de la aplicación

Con el entorno virtual activado y desde la raíz del proyecto:

```bash
streamlit run app.py
# python -m streamlit run app.py
```

Streamlit mostrará en la terminal una dirección local similar a:

```
Local URL: http://localhost:8501
```

Abrir esa dirección en el navegador. Para detener la aplicación, presionar
`Ctrl + C` en la terminal.

## 15. Uso básico de la interfaz

1. **Panel de configuración (barra lateral)**
   * *Escenario a ejecutar*: Escenario 1, Escenario 2, Escenario 3 o
     “Comparar los tres escenarios”.
   * *Cantidad de clientes*: por defecto 1000. Con más clientes los resultados
     suelen acercarse más a la teoría, pero la simulación tarda un poco más.
   * *Semilla aleatoria*: por defecto 42. Si se cambia, cambian los resultados;
     si se repite la misma semilla con la misma configuración, los resultados
     son idénticos.
   * *Iniciar simulación*: ejecuta el modelo.
2. **Resultados principales**: tarjetas con la utilización teórica, el tiempo
   promedio de espera simulado (Wq), el tamaño promedio de la cola simulado (Lq)
   y la cantidad de clientes atendidos.
3. **Tabla comparativa**: columnas teóricas y simuladas para cada escenario. Las
   columnas cuyo nombre termina en *teórica* provienen de las fórmulas; el resto
   proviene de la simulación.
4. **Visualización**: evolución del tamaño de la cola en el tiempo e histograma de
   los tiempos de espera. Al comparar los tres escenarios se añaden las gráficas
   comparativas de Wq y de Lq.
5. **Datos de clientes**: sección desplegable con la tabla individual (llegada,
   inicio de servicio, espera, servicio, salida y tiempo en el sistema). Se
   muestran como máximo los primeros 200 clientes para no saturar la interfaz.

## 16. Interpretación de resultados y gráficas

* **Evolución del tamaño de la cola**: muestra cuántos clientes esperan en cada
  instante. La línea discontinua es el valor teórico de `Lq`. Cuanto más cerca
  está λ de μ, más alta y más irregular es la serie.
* **Histograma de tiempos de espera**: distribución de las esperas individuales.
  La línea negra discontinua es `Wq` teórica y la línea roja la espera promedio
  simulada. En el escenario 1 muchas observaciones valen cero (el servidor suele
  estar libre); en el escenario 3 la distribución se desplaza hacia la derecha.
* **Gráficas comparativas**: barras grises para el valor teórico y azules para el
  simulado, en los tres escenarios. Permiten ver cómo crecen Wq y Lq al aumentar
  λ.
* **ρ (utilización)**: proporción del tiempo en que el servidor está ocupado. En
  el escenario 3, ρ ≈ 0.967, es decir, el servidor está ocupado casi todo el
  tiempo y por eso la cola es mucho mayor.

## 17. Limitaciones del modelo y diferencias entre teoría y simulación

* **Variabilidad aleatoria**: la simulación usa números aleatorios, por lo que
  cada ejecución produce valores distintos. Las diferencias disminuyen al aumentar
  la cantidad de clientes.
* **Tamaño de la muestra**: con pocos clientes (por ejemplo 100) las diferencias
  frente a la teoría pueden ser grandes; con 10 000 o más suelen ser pequeñas.
* **Periodo transitorio**: la teoría describe el estado estacionario, pero la
  simulación comienza con el servidor vacío. Ese arranque “a cola vacía” hace que
  los promedios simulados sean ligeramente menores que los teóricos.
* **Cerca de la saturación**: en el escenario 3 (ρ ≈ 0.967) la cola es muy
  sensible al azar y a la cantidad de clientes; se necesitan simulaciones largas
  para acercarse al valor teórico. Que el resultado simulado sea menor que el
  teórico en este escenario es esperable y no indica un error del modelo.
* **Delimitación de la simulación**: los promedios temporales se calculan en el
  intervalo `[0, T]`, con `T` = instante en que sale el último cliente. Otra
  delimitación razonable (por ejemplo, empezar a observar tras el primer cliente)
  daría valores ligeramente distintos.
* **Errores numéricos**: los tiempos se manejan en punto flotante; las
  comparaciones internas usan tolerancias muy pequeñas.
* **El modelo no incluye**: capacidad máxima de la cola, prioridades, varios
  servidores, clientes que se retiran sin ser atendidos ni tiempos de servicio
  no exponenciales.

En resumen: **no se exige que la simulación coincida exactamente con la teoría**.
Lo que se busca es que los valores simulados sean coherentes y se aproximen a los
teóricos cuando la simulación es suficientemente larga.

## 18. Uso de Git y recomendaciones para el trabajo colaborativo

El repositorio todavía no existe; cuando el grupo lo cree, estas son las
recomendaciones:

1. Inicializar el repositorio en la raíz del proyecto (`git init`) y hacer el
   primer commit con el código, las pruebas, `requirements.txt`, `.gitignore` y
   `README.md`.
2. **No** agregar `.venv/`, `venv/`, `__pycache__/` ni ninguna carpeta de
   dependencias: el archivo `.gitignore` ya las excluye.
3. Trabajar con una rama por integrante, por ejemplo:

```bash
git checkout -b feature/nombre_integrante
```

4. Integrar los cambios en `develop` y finalmente en `main`, según la estrategia
   que acuerde el grupo.
5. Antes de cada commit revisar `git status` y `git diff` para no subir archivos
   temporales ni datos personales.
6. Los commits deben realizarlos los integrantes del grupo; la asistencia de IA
   se documenta en el README, no como autor de los commits.

## 19. Declaración del uso de inteligencia artificial

* **Herramienta utilizada**: [OpenCode](https://opencode.ai), asistente de
  programación basado en inteligencia artificial, ejecutado en la terminal.
* **Uso dado**: la IA se utilizó como apoyo para **estructurar** el proyecto
  (arquitectura MVC), **implementar** el código base (modelo con SimPy, métricas,
  controlador, vistas con Streamlit y Matplotlib), **redactar** las pruebas
  automatizadas, **redactar** este README y **revisar** errores durante el
  desarrollo.
* **Supervisión humana**: los integrantes del grupo deben **comprender** cada
  archivo, **ejecutar** las pruebas, **comprobar** que los resultados provienen de
  ejecuciones reales del modelo y **validar** los valores antes de presentarlos.
  Ningún resultado de este proyecto fue inventado: todo dato que aparece en la
  aplicación se calcula al ejecutarla.
* **Prompt principal utilizado**: se encuentra transcrito íntegramente en el
  **Anexo A** de este README.

---

## Anexo A. Prompt maestro utilizado con la IA

El siguiente es el texto completo del prompt maestro que se entregó a OpenCode
para generar el proyecto (instrucciones del docente y de la práctica incluidas).
Si durante el desarrollo se realizaron ajustes o aclaraciones, deben registrarse
aquí para que la declaración siga siendo fiel a lo ocurrido.

```markdown
<!-- PROMPT_MAESTRO_INICIO -->

## PROMPT MAESTRO PARA OPENCODE: PRÁCTICA 03 DE SIMULACIÓN M/M/1

> Ojo, todavía no quiero que crees repositorios de github ni locales, tu enfocate en el codigo, ya que nosotros los integrantes del proyecto, nos encargaremos en un futuro de crear un repositorio y subirlo a github. Entonces cualquier instruccion que veas relacionada de manera directa con un repositorio de git ignorala, a escepcion de que por ejemplo simplemente sea como contexto de trabajo (por ejemplo: en un futuro se usara git, entonces trata de adaptar...). Entonces así procede.

### Rol y objetivo

Actúa como desarrollador de software Python con experiencia en simulación de eventos discretos, SimPy, arquitectura MVC y desarrollo de aplicaciones educativas.

Tu tarea es **implementar directamente en el repositorio el proyecto completo y funcional** correspondiente a la práctica 03 de la asignatura Simulación, de quinto ciclo de la carrera de Computación de la Universidad Nacional de Loja.

El proyecto consiste en simular un sistema de líneas de espera M/M/1, comparar sus resultados con las métricas teóricas y visualizar el comportamiento de la cola y los tiempos de espera.

No te limites a proponer una arquitectura, generar un plan o mostrar ejemplos. Inspecciona el entorno de trabajo, crea los archivos necesarios, implementa la aplicación, ejecuta las pruebas disponibles, corrige los errores encontrados y deja el repositorio listo para que los estudiantes puedan ejecutarlo, comprenderlo y exponerlo en clase.

### Alcance actual del trabajo

En esta fase se desarrolla exclusivamente el software y los archivos necesarios para su ejecución y mantenimiento.

**Sí debes crear:**
- Código fuente completo y modular.
- Interfaz gráfica web local sencilla.
- Pruebas automatizadas.
- `requirements.txt`.
- `README.md` con las instrucciones y el prompt de IA utilizado.
- `.gitignore`.
- Archivos de configuración estrictamente necesarios.

**No debes elaborar todavía:**
- Informe académico en PDF o Word.
- Artículo científico en formato IEEE.
- Documento de metodología de la práctica.
- Conclusiones académicas definitivas.
- Capturas de pantalla o evidencias inventadas.
- Presentación de diapositivas o video de exposición.

No inventes resultados experimentales. Los resultados que aparezcan en la aplicación deben proceder de la ejecución real del modelo.

### Requisitos establecidos por el docente

1. Utilizar Python.
2. Utilizar SimPy para la simulación de eventos discretos.
3. Utilizar NumPy para generar variables aleatorias y Matplotlib para las gráficas.
4. Entregar varios archivos organizados mediante una arquitectura modular; no se acepta un único script monolítico.
5. Evidenciar el uso de patrones de diseño, preferentemente MVC.
6. Utilizar Git para el control de versiones.
7. Incluir `requirements.txt`.
8. No subir al repositorio entornos virtuales ni carpetas de dependencias.
9. Incluir un `README.md` que explique el proyecto, las dependencias, la instalación, la ejecución, la estructura de carpetas y el uso de inteligencia artificial.
10. Mantener el código sencillo, legible y apropiado para estudiantes que deben explicar personalmente su funcionamiento.

No introduzcas capas, abstracciones, patrones adicionales ni dependencias innecesarias. La arquitectura debe ser suficientemente organizada para cumplir las exigencias del docente, pero lo bastante sencilla para aprenderla y defenderla en clase.

### Descripción del sistema que debe simularse

El modelo M/M/1 representa una cola con las siguientes características:

- Primera M: los tiempos entre llegadas siguen una distribución exponencial, equivalente a un proceso de llegadas de Poisson.
- Segunda M: los tiempos de servicio siguen una distribución exponencial.
- 1: existe un único servidor.
- Disciplina de atención FIFO: primero en llegar, primero en ser atendido.
- Los tiempos entre llegadas y de servicio se expresan en una unidad de tiempo consistente.

Define los parámetros:

- `lambda_rate`: tasa media de llegada de clientes, λ.
- `mu_rate`: tasa media de servicio, μ.
- `num_customers`: cantidad de clientes que se generarán en cada ejecución.
- `seed`: semilla utilizada para reproducir los resultados aleatorios.

Las tasas se expresan en clientes por unidad de tiempo. Los tiempos generados deben expresarse en esa misma unidad de tiempo.

Genera los tiempos aleatorios mediante distribuciones exponenciales parametrizadas por la tasa correspondiente:

- Tiempo entre llegadas: exponencial con escala `1 / lambda_rate`.
- Tiempo de servicio: exponencial con escala `1 / mu_rate`.

Utiliza SimPy para gestionar el reloj de simulación, las llegadas, las solicitudes del servidor, la espera y la atención de cada cliente. No sustituyas el motor de simulación por simples fórmulas o cálculos estadísticos desconectados del modelo.

### Escenarios obligatorios

Implementa los tres escenarios definidos en la guía de la práctica:

| Escenario | λ | μ | Característica |
|---|---:|---:|---|
| 1 | 2.0 | 3.0 | Sistema estable |
| 2 | 2.5 | 3.0 | Mayor utilización |
| 3 | 2.9 | 3.0 | Cerca de la saturación |

La aplicación debe permitir ejecutar cada escenario individualmente y ejecutar los tres en una misma operación para facilitar la comparación.

Permite modificar la cantidad de clientes y la semilla aleatoria desde la interfaz. Los valores de λ y μ deben poder seleccionarse mediante los escenarios predefinidos. Si decides permitir valores personalizados, valida las entradas y conserva siempre los escenarios originales como opciones claramente identificadas.

No alteres silenciosamente los parámetros de los escenarios obligatorios.

### Cálculos teóricos obligatorios

Implementa los cálculos teóricos en una función o módulo independiente de la interfaz gráfica.

Las fórmulas que deben utilizarse son:

Utilización teórica del servidor:

`rho = lambda_rate / mu_rate`

Número promedio de clientes en el sistema:

`L = lambda_rate / (mu_rate - lambda_rate)`

Número promedio de clientes en la cola:

`Lq = lambda_rate**2 / (mu_rate * (mu_rate - lambda_rate))`

Tiempo promedio de permanencia en el sistema:

`W = 1 / (mu_rate - lambda_rate)`

Tiempo promedio de espera en la cola:

`Wq = lambda_rate / (mu_rate * (mu_rate - lambda_rate))`

Condición de estabilidad:

`lambda_rate < mu_rate`

**Importante:** la utilización del servidor es λ/μ, no μ/λ. Implementa exactamente las fórmulas anteriores.

Antes de calcular las métricas, comprueba que las tasas sean positivas y que `lambda_rate < mu_rate`. Si el sistema no es estable, muestra un mensaje comprensible y no calcules las métricas estacionarias como si fueran válidas.

Las métricas teóricas se expresan en unidades coherentes con las tasas de llegada y servicio.

### Implementación de la simulación

Implementa un modelo funcional que reproduzca el comportamiento de una cola M/M/1.

El proceso de simulación debe realizar, como mínimo, estas operaciones:

1. Crear un entorno SimPy.
2. Crear un recurso con capacidad de un servidor.
3. Generar clientes según los tiempos entre llegadas.
4. Registrar el instante de llegada de cada cliente.
5. Solicitar el servidor y respetar la disciplina FIFO.
6. Registrar cuándo comienza la atención.
7. Calcular el tiempo de espera en la cola.
8. Generar y registrar el tiempo de servicio.
9. Registrar cuándo termina la atención.
10. Recopilar los datos necesarios para calcular las métricas simuladas.
11. Devolver los resultados en una estructura de datos clara.

Cada cliente debe tener, como mínimo, los siguientes datos:

- Identificador.
- Tiempo de llegada.
- Inicio del servicio.
- Tiempo de espera en la cola.
- Duración del servicio.
- Tiempo de salida.
- Tiempo total en el sistema.

Para cada cliente, calcula:

`waiting_time = service_start - arrival_time`

`system_time = departure_time - arrival_time`

Comprueba que los tiempos sean coherentes: el tiempo de espera no puede ser negativo, el tiempo total en el sistema debe incluir la espera y el servicio, y el servidor nunca debe atender a dos clientes simultáneamente.

#### Finalización de la simulación

Utiliza una cantidad definida de clientes y permite que todos los clientes generados terminen su atención antes de calcular las métricas finales. Así se evita excluir arbitrariamente a los clientes que permanezcan en la cola al alcanzar un horizonte de tiempo fijo.

Documenta esta decisión en el README, porque las métricas experimentales dependen de cómo se delimite la simulación.

#### Métricas simuladas

Calcula como mínimo:

- Tiempo promedio de espera en la cola.
- Tamaño promedio de la cola.
- Número de clientes atendidos.
- Tiempo promedio de permanencia en el sistema.
- Utilización experimental del servidor, si puede calcularse correctamente.

El tiempo promedio de espera se obtiene a partir de los tiempos de espera de los clientes simulados.

Para el tamaño promedio de la cola, utiliza una medición temporal: integra el número de clientes esperando a lo largo del tiempo y divide el área acumulada por el tiempo total de observación. No calcules el promedio de unas pocas observaciones instantáneas como si fuese el promedio temporal real.

Implementa el seguimiento de la cola mediante eventos del modelo SimPy. Actualiza el área acumulada cada vez que cambie la cantidad de clientes esperando y al finalizar la observación.

Define y documenta con claridad el intervalo de observación utilizado para calcular el tamaño promedio de la cola y la utilización experimental.

No confundas el tamaño promedio de la cola `Lq` con el número promedio de clientes en todo el sistema `L`.

#### Aleatoriedad reproducible

Utiliza una semilla controlada para que una ejecución pueda reproducirse con los mismos parámetros y la misma configuración.

Evita que la interfaz y el modelo dependan de un generador aleatorio global compartido sin control.

Si se ejecutan los tres escenarios, conserva la configuración elegida y muestra claramente la semilla utilizada. Si las comparaciones emplean semillas diferentes, indícalo; de preferencia, utiliza una configuración reproducible por escenario.

### Comparación de resultados

Para cada escenario, calcula los valores teóricos y los simulados que correspondan.

Presenta una tabla comparativa con, al menos, estas columnas:

- Escenario.
- λ.
- μ.
- ρ teórica.
- L teórica.
- Lq teórica.
- W teórica.
- Wq teórica.
- Tiempo promedio de espera simulado.
- Tamaño promedio de la cola simulado.

Puedes añadir el tiempo promedio en el sistema y la utilización experimental para enriquecer la comparación, siempre que no compliques innecesariamente el programa.

Identifica explícitamente cuáles son valores teóricos y cuáles proceden de la simulación.

Utiliza un número razonable de decimales en la interfaz. Conserva suficiente precisión internamente.

No exijas que los resultados simulados coincidan exactamente con los teóricos. Explica en la interfaz o en el README que las diferencias se deben a la variabilidad aleatoria, el tamaño de la muestra y las condiciones de observación.

### Gráficas obligatorias

Utiliza Matplotlib para generar las gráficas.

Incluye, como mínimo:

1. Evolución del tamaño de la cola durante la simulación.
2. Distribución de los tiempos de espera de los clientes, por ejemplo, mediante un histograma.
3. Comparación del tiempo promedio de espera simulado entre los tres escenarios.
4. Comparación del tamaño promedio de la cola simulado entre los tres escenarios.

Si resulta conveniente, incorpora líneas de referencia que permitan comparar las métricas teóricas y simuladas. No mezcles métricas con unidades diferentes en un mismo eje sin explicarlo.

Las gráficas deben tener título, ejes etiquetados y unidades. Los gráficos comparativos deben identificar claramente los escenarios.

No generes gráficas con datos ficticios ni utilices valores teóricos como si fueran observaciones simuladas.

Asegúrate de que las gráficas se puedan visualizar correctamente en la interfaz. Si guardas archivos de imagen, utiliza una ubicación temporal o una carpeta de resultados claramente identificada y evita sobrescribir archivos de otros usos sin necesidad.

### Interfaz gráfica

Desarrolla un frontend web local sencillo utilizando **Streamlit**.

Esta es una decisión de diseño para facilitar la demostración del proyecto: no es necesario construir una aplicación con React, un servidor API independiente, JavaScript personalizado ni una arquitectura distribuida.

La aplicación debe poder ejecutarse en el navegador del propio equipo, sin servicios externos y sin necesitar una conexión a internet una vez instaladas las dependencias.

La interfaz debe estar en español y tener un diseño limpio, académico y fácil de explicar.

Organiza la pantalla de la siguiente manera:

#### Encabezado

Muestra:

- Simulación de un sistema de líneas de espera M/M/1.
- Asignatura: Simulación.
- Carrera: Computación.
- Universidad Nacional de Loja.
- Una breve explicación del propósito de la aplicación.

No inventes nombres de integrantes ni datos personales. Deja los datos de autoría para que el grupo los complete en el README si corresponde.

#### Panel de configuración

Incluye controles para:

- Seleccionar uno de los tres escenarios o ejecutar la comparación de todos.
- Establecer la cantidad de clientes.
- Establecer la semilla aleatoria.
- Iniciar la simulación mediante un botón.

Valida las entradas antes de ejecutar el modelo. Utiliza valores predeterminados razonables y explica qué representan.

#### Resultados principales

Muestra tarjetas o indicadores con los resultados relevantes:

- Utilización teórica.
- Tiempo promedio de espera simulado.
- Tamaño promedio de la cola simulado.
- Número de clientes atendidos.

Añade una tabla que compare los resultados teóricos y simulados.

#### Visualización

Presenta las gráficas obligatorias debajo de los resultados. Si se ejecutan los tres escenarios, muestra los gráficos comparativos y permite distinguir claramente cada escenario.

#### Datos de clientes

Añade una sección desplegable opcional para consultar una tabla con los datos individuales de los clientes. No muestres miles de filas automáticamente; utiliza paginación o una vista limitada si resulta necesario.

#### Explicación educativa

Incluye una sección breve que explique:

- Qué es el modelo M/M/1.
- Qué representan λ, μ y ρ.
- Qué diferencia existe entre L y Lq.
- Qué diferencia existe entre W y Wq.
- Por qué aumenta la espera cuando λ se aproxima a μ.

No conviertas la aplicación en un documento teórico extenso. La explicación debe ayudar a entender y defender el código.

### Arquitectura y patrones de diseño

Utiliza una arquitectura MVC sencilla, separando las responsabilidades.

Organiza el proyecto de manera semejante a esta estructura:

`simulacion_mm1/`

- `app.py`: punto de entrada de la interfaz Streamlit.
- `model/`
  - `__init__.py`
  - `queue_model.py`: simulación de eventos discretos y generación de clientes.
  - `metrics.py`: métricas teóricas y cálculos estadísticos de los resultados.
- `controller/`
  - `__init__.py`
  - `simulation_controller.py`: coordina la ejecución, valida parámetros y prepara los resultados.
- `view/`
  - `__init__.py`
  - `dashboard.py`: componentes de presentación, tablas, indicadores y gráficas.
- `tests/`
  - `test_metrics.py`
  - `test_simulation.py`
- `requirements.txt`
- `.gitignore`
- `README.md`

Puedes ajustar esta estructura si existe una razón técnica concreta, pero conserva la separación entre modelo, controlador y vista. No añadas archivos vacíos ni carpetas sin propósito.

#### Modelo

El modelo no debe depender de Streamlit ni importar componentes de interfaz. Debe ejecutar la simulación y devolver los datos.

#### Controlador

El controlador debe coordinar el modelo y las métricas, validar parámetros y preparar resultados para la presentación. No debe contener el código de dibujo de la interfaz.

#### Vista

La vista debe encargarse de presentar los controles, resultados, tablas y gráficas. Puede utilizar Streamlit y Matplotlib.

#### Punto de entrada

`app.py` debe ser sencillo: iniciar la aplicación y conectar sus componentes. Evita concentrar toda la lógica en este archivo.

#### Patrones adicionales

No es obligatorio añadir más patrones de diseño si MVC ya está aplicado correctamente. Prioriza un diseño fácil de explicar, sin clases abstractas, fábricas, repositorios o servicios adicionales que no aporten una ventaja real a esta práctica.

Utiliza funciones y clases únicamente cuando ayuden a separar responsabilidades o a comprender el modelo.

### Pruebas automatizadas

Incluye pruebas con la biblioteca estándar `unittest`, de modo que no sea obligatorio instalar otra dependencia exclusivamente para las pruebas.

Prueba como mínimo los siguientes casos:

1. Las métricas teóricas son correctas para λ = 2.0 y μ = 3.0.
2. La utilización calculada es λ/μ.
3. El sistema rechaza tasas iguales o mayores de llegada que de servicio para las métricas estacionarias.
4. El modelo genera la cantidad de clientes solicitada.
5. Todos los clientes generados terminan siendo atendidos.
6. Los tiempos de espera y permanencia son coherentes.
7. La capacidad del servidor es uno.
8. La ejecución con la misma configuración y semilla produce resultados reproducibles.
9. Los resultados no contienen valores imposibles, como tiempos negativos o promedios indefinidos en una simulación válida.
10. Los tres escenarios predefinidos pueden ejecutarse correctamente.

Comprueba también los casos de parámetros inválidos, como cantidades de clientes iguales a cero, tasas no positivas y valores que no sean válidos.

No bases las pruebas en exigir que una simulación aleatoria reproduzca exactamente los valores teóricos. Las pruebas de métricas deterministas sí deben comprobar resultados matemáticos exactos, dentro de una tolerancia numérica razonable.

### Dependencias y entorno virtual

El proyecto debe poder instalarse en un entorno virtual independiente.

Utiliza las siguientes dependencias directas:

- SimPy.
- NumPy.
- Matplotlib.
- Streamlit.

No instales bibliotecas adicionales si no son necesarias.

Genera un `requirements.txt` con versiones compatibles y verificadas de las dependencias que realmente utiliza el proyecto. Comprueba la instalación en un entorno virtual limpio. No inventes números de versión ni incluyas todas las bibliotecas globales del equipo.

El README debe explicar cómo crear y activar un entorno virtual, instalar dependencias y ejecutar la aplicación tanto en Linux como, si es sencillo, en Windows.

La ejecución debe seguir un flujo semejante a este:

1. Clonar el repositorio.
2. Entrar en la carpeta del proyecto.
3. Crear el entorno virtual.
4. Activar el entorno virtual.
5. Instalar las dependencias.
6. Ejecutar las pruebas.
7. Iniciar la aplicación con Streamlit.
8. Abrir la dirección local que indique Streamlit.

Adapta los comandos a la estructura real del proyecto y comprueba que sean correctos.

No incluyas la carpeta del entorno virtual dentro del repositorio.

### Git y control de versiones

Respeta el repositorio existente si ya hay uno. Antes de realizar operaciones Git, inspecciona el estado actual para evitar sobrescribir cambios de los estudiantes.

Si el repositorio está vacío o todavía no existe, prepara el proyecto para que pueda inicializarse y versionarse correctamente.

El `.gitignore` debe excluir, como mínimo:

- `.venv/`
- `venv/`
- `env/`
- `__pycache__/`
- `*.py[cod]`
- Archivos `.pytest_cache/` y otros directorios de caché si se generan.
- Archivos temporales del editor.
- Secretos y archivos locales de configuración que no deban publicarse.
- Resultados generados que no deban formar parte del código fuente.

No excluyas el código, las pruebas, el README ni el archivo `requirements.txt`.

No añadas carpetas de entornos virtuales, dependencias descargadas ni archivos binarios innecesarios al repositorio.

El proyecto debe permitir el trabajo colaborativo mediante ramas individuales, por ejemplo `feature/nombre_integrante`, y la integración posterior a `develop` o `main`, según la estrategia que utilice el grupo.

No inventes los nombres de los integrantes. No hagas push, merges ni commits en nombre de los estudiantes sin autorización explícita. Deja los cambios preparados para que el grupo pueda revisarlos y registrar sus propios commits.

### README.md obligatorio

Redacta un README en español, claro y orientado a estudiantes principiantes.

Debe contener las siguientes secciones:

1. Nombre del proyecto.
2. Descripción del problema y propósito de la simulación.
3. Objetivo general de la aplicación.
4. Tecnologías utilizadas.
5. Descripción del modelo M/M/1.
6. Parámetros y escenarios disponibles.
7. Fórmulas de las métricas teóricas.
8. Arquitectura MVC y responsabilidades de los archivos.
9. Árbol real de carpetas.
10. Requisitos previos.
11. Instalación paso a paso.
12. Activación del entorno virtual.
13. Instalación de dependencias.
14. Ejecución de las pruebas.
15. Inicio de la aplicación.
16. Uso básico de la interfaz.
17. Interpretación de resultados y gráficas.
18. Limitaciones del modelo y explicación de las diferencias entre teoría y simulación.
19. Uso de Git y recomendaciones para el trabajo colaborativo.
20. Declaración del uso de inteligencia artificial.

En la declaración de inteligencia artificial, identifica OpenCode como la herramienta utilizada para asistir en el desarrollo y documenta el prompt principal empleado.

**Incluye en el README el texto completo del prompt maestro utilizado para generar el proyecto**, es decir, este prompt de instrucciones, o una copia íntegra del prompt que efectivamente se utilizó si posteriormente se modificó. No afirmes que se usó un prompt diferente del real. Puedes colocar el contenido extenso en un apéndice del README para no interrumpir las instrucciones de instalación.

Explica que la IA fue utilizada como apoyo para estructurar, implementar y revisar el código, y que los integrantes deben comprender, comprobar y validar los resultados antes de presentar el proyecto.

No inventes pruebas realizadas, resultados obtenidos, integrantes ni evidencias.

### Criterios de calidad y comprensión

El proyecto debe priorizar la facilidad de aprendizaje y la demostración en clase.

- Utiliza nombres de variables y funciones descriptivos.
- Mantén las funciones relativamente pequeñas.
- Incluye comentarios únicamente cuando ayuden a comprender una decisión o un cálculo.
- Evita comentarios que repitan literalmente lo que ya dice el código.
- No uses código excesivamente compacto.
- No uses patrones innecesarios ni una arquitectura sobredimensionada.
- No introduzcas bases de datos, autenticación, servicios externos ni persistencia innecesaria.
- No dependas de una API externa ni de servicios en la nube.
- No dejes funciones importantes con `TODO`, `pass` o implementaciones ficticias.
- No reemplaces la simulación real por datos de ejemplo.
- No ocultes excepciones que impidan detectar fallos.
- Presenta errores de parámetros en español, con mensajes útiles para el usuario.

El código debe ser suficientemente sencillo para que un estudiante pueda explicar en clase qué hace el modelo, cómo se organiza MVC, cómo se genera una llegada, cómo se solicita el servidor y cómo se obtienen las métricas.

### Flujo de trabajo que debes seguir

Ejecuta el trabajo en este orden:

**Fase 1. Inspección**
- Inspecciona el directorio de trabajo y el estado de Git.
- Comprueba si ya existen archivos que deban conservarse.
- No sobrescribas cambios previos sin revisarlos.
- Identifica el entorno de Python disponible.

**Fase 2. Diseño**
- Define la estructura MVC mínima.
- Identifica las responsabilidades de cada módulo.
- Define las estructuras de datos para los clientes y los resultados.
- Comprueba que el diseño permita obtener las métricas teóricas y simuladas sin duplicar cálculos.

**Fase 3. Implementación**
- Crea el modelo de simulación.
- Implementa las métricas teóricas.
- Implementa el controlador.
- Implementa las vistas, las tablas y las gráficas.
- Construye la interfaz Streamlit.
- Crea las pruebas.
- Escribe el README y el `.gitignore`.

**Fase 4. Instalación y verificación**
- Crea o utiliza un entorno virtual aislado.
- Instala las dependencias necesarias.
- Comprueba las importaciones.
- Ejecuta todas las pruebas automatizadas.
- Corrige los errores y vuelve a ejecutar las pruebas.
- Ejecuta los tres escenarios.
- Comprueba que las métricas sean finitas y coherentes.
- Comprueba que la interfaz pueda iniciarse y que sus componentes no dependan de archivos inexistentes.
- Verifica que `requirements.txt` sea suficiente para reproducir el entorno.

**Fase 5. Revisión final**
- Revisa el árbol de carpetas real.
- Comprueba que no se hayan incluido entornos virtuales ni cachés en Git.
- Comprueba que los comandos del README coincidan con la implementación real.
- Comprueba que la aplicación no contenga datos ficticios presentados como resultados reales.
- Comprueba que el prompt de IA esté documentado.
- Verifica que el proyecto pueda ejecutarse siguiendo únicamente las instrucciones del README.

Si alguna operación no puede realizarse por limitaciones del entorno, indícalo claramente. No afirmes que una prueba se ejecutó si no pudiste ejecutarla.

### Criterios de aceptación

Considera el trabajo terminado únicamente cuando:

- Existe una aplicación ejecutable en Python.
- Se utiliza SimPy para simular una cola M/M/1 real.
- Se utiliza NumPy para la generación de variables aleatorias.
- Se utiliza Matplotlib para generar las gráficas.
- Se puede ejecutar cada uno de los tres escenarios establecidos.
- Se calculan correctamente las métricas teóricas.
- Se obtienen las métricas simuladas y se comparan con las teóricas.
- Se puede consultar la evolución de la cola y la distribución de los tiempos de espera.
- Existe una interfaz local en español.
- La arquitectura MVC está aplicada de forma real y comprensible.
- Las pruebas automatizadas pasan.
- Existe un `requirements.txt` verificable.
- Existe un README completo con instalación, ejecución, arquitectura y prompt de IA.
- El repositorio está preparado para el trabajo colaborativo con Git.
- No se incluyen entornos virtuales ni dependencias descargadas.
- No quedan errores conocidos sin documentar ni funciones esenciales sin implementar.

### Instrucción final

Empieza inspeccionando el repositorio y continúa con la implementación completa. Toma decisiones técnicas sencillas cuando no haya una instrucción específica, priorizando la corrección matemática, la reproducibilidad, la claridad y la facilidad de exposición.

No te detengas después de generar el plan. Implementa, ejecuta, verifica y corrige todo lo que sea posible en el entorno disponible.

Al terminar, presenta un resumen breve con:

1. Qué se implementó.
2. Cómo está organizado el proyecto.
3. Cómo se instala y ejecuta.
4. Qué pruebas se ejecutaron y cuáles pasaron.
5. Qué comprobaciones no pudieron realizarse, si las hubiera.
6. Qué archivos deben revisarse antes de realizar los commits del grupo.

No empieces a elaborar el informe académico final. La entrega de esta fase es el código fuente funcional, sus pruebas y los archivos necesarios para ejecutarlo y mantenerlo.

<!-- PROMPT_MAESTRO_FIN -->
```
