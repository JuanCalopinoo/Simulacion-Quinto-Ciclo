# APE 4: simulación SIR con Python y SimPy

Implementación de la parte Python de la práctica: simulación discreta por agentes,
exportación CSV para NetLogo y gráfica de susceptibles, infectados y recuperados.
Requiere Python 3.10 o posterior.

## Instalación y ejecución

Desde esta carpeta:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

En Windows, activa el entorno con `.venv\Scripts\activate`.

La ejecución predeterminada usa N=100, S(0)=95, I(0)=5, R(0)=0,
beta=0.30, gamma=0.10, 100 pasos y semilla 42. Produce:

- `datos/resultados_python.csv`: encabezado y 101 registros, desde t=0 hasta t=100.
- `graficas/sir_evolucion.png`: las tres curvas de evolución.
- Resumen por consola con pico de infectados, estado final y tiempo de cómputo del motor.

Los archivos se sobrescriben al repetir la ejecución con las mismas rutas.
Las rutas predeterminadas se resuelven respecto de la carpeta del proyecto.

## Motor y reglas

SimPy programa cada paso mediante `Environment`, un proceso y `timeout(1)`.
El estado inicial se registra antes del primer evento. Cada llamada a `ejecutar`
crea su propia población, entorno y generador aleatorio.

En cada paso, cada infectado del estado anterior elige un contacto aleatorio
entre los demás agentes. Si ese contacto era susceptible, se contagia con
probabilidad beta. Cada infectado original se recupera con probabilidad gamma.
Los cambios se escriben en una copia y se aplican simultáneamente: un nuevo
infectado no contagia ni se recupera hasta el paso siguiente. Un agente
contagiado por varios infectados se cuenta una sola vez.

La selección de un contacto por infectado es una decisión explícita: la guía
no especifica cuántos contactos escoger. Se mantiene para la corrida evaluada.
No se resuelven directamente las ecuaciones diferenciales; beta/gamma=3 es
la referencia teórica, no un resultado exacto exigible a una corrida aleatoria.
No hay nacimientos, muertes ni reinfecciones. Siempre se verifica N=S+I+R,
S no aumenta y R no disminuye. Se continúa registrando hasta t=100 aunque
ya no existan infectados.

## CSV para NetLogo

El contrato de datos es:

```csv
tiempo,susceptibles,infectados,recuperados
0,95,5,0
```

Archivo UTF-8, separado por comas, con encabezado y cuatro columnas enteras,
sin índice adicional. Copia `datos/resultados_python.csv` a la carpeta del `.nlogo`
o genera el archivo directamente allí:

```bash
python main.py --salida "/ruta/al/proyecto/netlogo"
```

NetLogo debe saltar el encabezado y leer las columnas en ese orden. El CSV
contiene todo lo necesario para graficar las tres series; el PNG no se importa.
Este proyecto no crea ni modifica archivos NetLogo.

## Código y pruebas

- `config.py`: valores predeterminados y validación.
- `modelo/`: población, estados y transiciones simultáneas.
- `simulacion/`: motor SimPy y validación de registros.
- `resultados/`: CSV y gráfica con Matplotlib y NumPy.
- `pruebas/`: pruebas automáticas.

```bash
python -m unittest discover -s pruebas -v
```

Para consultar opciones: `python main.py --help`. Los parámetros modificables
sirven para experimentar; la entrega usa los valores predeterminados de la guía.
Para futuras comparaciones, las otras implementaciones deberán compartir también
la regla de contactos. Compartir semilla entre lenguajes no garantiza series idénticas.
