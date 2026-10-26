# Simulación de un modelo matemático de lluvia

**Universidad Nacional de Loja (UNL) · Carrera de Computación · Simulación · Ciclo 5**  
**Práctica N.º 001: Construcción y simulación computacional de un modelo matemático**

Proyecto académico **exclusivamente en Python 3**, con **NumPy** y **Matplotlib** como únicas dependencias externas. Al ejecutar `main.py` se completan automáticamente las dos tablas solicitadas, se guardan **seis gráficas PNG** y se genera un **PDF con la práctica resuelta**, además de un documento Markdown editable.

## Arquitectura

```text
simulacion_modelo_lluvia/
├── main.py                        # Punto de entrada: ejecuta todo
├── requirements.txt              # NumPy y Matplotlib
├── datos/
│   └── mediciones.csv            # Nueve registros originales de la guía
├── modelo/
│   ├── __init__.py
│   └── lluvia.py                  # Fórmulas, Tf, ajustes y clasificación
├── simulacion/
│   ├── __init__.py
│   └── ejecutar.py                # Carga/validación, ejecución, CSV, resumen
├── graficas/
│   ├── __init__.py
│   ├── generar.py                 # Crea automáticamente seis PNG
│   └── 01_...06_*.png             # Salidas (regeneradas en cada ejecución)
├── reportes/
│   ├── __init__.py
│   └── crear_pdf.py               # Informe PDF y solución Markdown
├── pruebas/
│   └── test_modelo.py            # unittest: fórmulas, reglas y datos de guía
├── resultados/
│   ├── tabla_original.csv
│   ├── tabla_ajustado.csv
│   ├── comparacion_escenarios.csv
│   └── practica_01_resuelta.pdf
└── docs/
    ├── guia_original_firmada.pdf  # Copia sin modificar de la guía original
    └── practica_resuelta_editable.md
```

## Cómo ejecutar en Ubuntu/Linux

Abre una terminal en la carpeta **donde está `main.py`**. Si el ZIP se encuentra en `~/Descargas`:

```bash
cd ~/Descargas
unzip simulacion_modelo_lluvia.zip
cd simulacion_modelo_lluvia
```

Crea y activa un entorno virtual (una sola vez):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Si `venv` no está disponible, instálalo con `sudo apt update` y `sudo apt install python3-venv` y vuelve a intentar. Luego instala dependencias:

```bash
python3 -m pip install -r requirements.txt
```

**Ejecuta el proyecto** (no necesita compilación, Python es interpretado):

```bash
python3 main.py
```

El programa imprimirá los resultados en consola y **generará/actualizará automáticamente** seis archivos PNG en `graficas/`, tres CSV y un PDF en `resultados/`, y una solución Markdown en `docs/`.

Opcionalmente, para **abrir** también las gráficas en ventanas en un Linux con escritorio:

```bash
python3 main.py --mostrar
```

Para las pruebas automáticas:

```bash
python3 -m unittest discover -s pruebas -v
```

Para salir del entorno virtual:

```bash
deactivate
```

No existen `compilar.sh`, `run.sh` ni instaladores: solo los comandos manuales mostrados arriba.

## Modelo de la guía

Modelo original:

\[
I=0.5H+0.3N+0.2T_f
\]

- **H**: humedad porcentual dividida entre 100.
- **N**: nubosidad porcentual dividida entre 100.
- **Tf**: factor de temperatura de la tabla de la guía: 10 °C o menos -> 1.0; cada 2 °C adicionales disminuye 0.1 hasta 28 °C o más -> 0.1.
- Entre temperaturas tabuladas (p. ej., 15 °C y 17 °C), **se interpola linealmente**. La guía no especifica el método entre valores: es un supuesto declarado para cubrir los datos de la tabla.

Estados:

| Intervalo de I | Estado |
|---|---|
| I < 0.40 | Sin lluvia |
| 0.40 ≤ I < 0.60 | Baja posibilidad |
| 0.60 ≤ I < 0.75 | Lluvia probable |
| I ≥ 0.75 | Lluvia |

Modelo ajustado de **comparación** (la guía dice «ajuste» pero no define parámetros nuevos):

\[
I_{ajustado}=0.6H+0.3N+0.1T_f
\]

Este escenario da más peso a la humedad y menos al factor de temperatura. Los pesos siguen sumando 1. Es un **análisis de sensibilidad**, no una calibración meteorológica.

**Advertencias sobre el alcance:** la guía anuncia 24 horas, pero solo incluye **nueve** horarios de 06:00 a 22:00, por lo que no se inventan registros adicionales. Los índices y etiquetas provienen de una regla matemática académica: no son probabilidades observadas de precipitación. Por otro lado, las preguntas sobre `r` y `P₀` pertenecen a un **modelo exponencial diferente**, no a la ecuación de lluvia. En el reporte se responden aclarando esa distinción.

## Archivos de resultados

| Archivo | Contenido |
|---|---|
| `resultados/tabla_original.csv` | Tabla original completa, incluidos H, N, Tf, índice y categoría |
| `resultados/tabla_ajustado.csv` | Misma tabla con los parámetros ajustados |
| `resultados/comparacion_escenarios.csv` | Diferencias por horario y categorías de ambos casos |
| `resultados/practica_01_resuelta.pdf` | Informe listo para revisar, con tablas, análisis, preguntas y las seis figuras |
| `docs/practica_resuelta_editable.md` | Versión en texto editable de la resolución |
| `graficas/01_variables_atmosfericas.png` | Crecimiento/decrecimiento de humedad, nubosidad y temperatura |
| `graficas/02_factores_normalizados.png` | Comparación de H, N y Tf |
| `graficas/03_indice_y_umbrales.png` | Índice original y cuatro rangos de clasificación |
| `graficas/04_aportes_del_modelo.png` | Contribución de cada componente a I |
| `graficas/05_comparacion_escenarios.png` | Efecto del cambio de los pesos |
| `graficas/06_estados_por_hora.png` | Estados de ambos escenarios según hora |

## Validación matemática

Se comprueba el ejemplo dado en la guía: humedad 90 %, nubosidad 80 % y temperatura 18 °C produce `Tf = 0.6` e índice `0.81`.

La entrada `datos/mediciones.csv` puede cambiarse manteniendo el encabezado `hora,humedad,nubosidad,temperatura`, con filas ordenadas y horas `HH:MM` sin duplicados. Los gráficos, tablas y PDF se regenerarán a partir de ese CSV con el siguiente comando habitual:

```bash
python3 main.py
```

**Fuente:** *Guía de Actividades Práctico-Experimentales N.º 001*, asignatura Simulación, Universidad Nacional de Loja, 2026 (material adjunto por el estudiante).
