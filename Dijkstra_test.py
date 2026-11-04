import os
import math
import random
import shutil
import subprocess

from GrafoLib_Dijkstra import (
    grafoMalla, grafoErdosRenyi, grafoGilbert,
    grafoGeografico, grafoBarabasiAlbert, grafoDorogovtsevMendes
)

# ---------------------------------------------------------
#  Configuracion
# ---------------------------------------------------------
TAMANOS = [ 150]          # numero de nodos de cada grafo
FUENTE = 0                   # nodo fuente s para Dijkstra
PESO_MIN, PESO_MAX = 1, 10   # rango de pesos aleatorios de las aristas
SEMILLA = 42                 # None para resultados distintos en cada ejecucion
GENERAR_PNG = True           # si Graphviz esta instalado, tambien crea imagenes .png

CARPETA_GEN = os.path.join("resultados", "generados")   # grafos originales
CARPETA_DIJ = os.path.join("resultados", "dijkstra")    # arboles de Dijkstra
os.makedirs(CARPETA_GEN, exist_ok=True)
os.makedirs(CARPETA_DIJ, exist_ok=True)

if SEMILLA is not None:
    random.seed(SEMILLA)


def dimensionesMalla(n):
    # Busca filas x columnas con exactamente n nodos, lo mas cuadrada posible
    for filas in range(int(math.sqrt(n)), 0, -1):
        if n % filas == 0:
            return filas, n // filas


def renderizar(ruta_dot):
    # Convierte el .dot a .png con Graphviz (si esta instalado)
    if not GENERAR_PNG or shutil.which("dot") is None:
        return None
    ruta_png = ruta_dot.replace(".dot", ".png")
    subprocess.run(["dot", "-Tpng", ruta_dot, "-o", ruta_png], check=True)
    return ruta_png


def procesar(nombre, g, n):
    # 1) Pesos aleatorios y .dot del grafo generado
    g.asignarPesosAleatorios(PESO_MIN, PESO_MAX)
    ruta_gen = os.path.join(CARPETA_GEN, f"{nombre}_{n}.dot")
    g.guardarGraphViz(ruta_gen, f"{nombre}_{n}")
    renderizar(ruta_gen)

    # 2) Dijkstra desde la fuente y .dot del arbol de caminos mas cortos
    arbol = g.Dijkstra(FUENTE)
    ruta_dij = os.path.join(CARPETA_DIJ, f"{nombre}_{n}_dijkstra.dot")
    arbol.guardarGraphViz(ruta_dij, f"{nombre}_{n}_Dijkstra")
    renderizar(ruta_dij)

    # 3) Resumen en consola
    alcanzados = arbol.numeroNodos()
    lejano = max(arbol.nodos.values(), key=lambda x: x.distancia)
    print(f"  {nombre:<20} nodos={g.numeroNodos():>4}  aristas={g.numeroAristas():>5}  "
          f"alcanzados desde s={alcanzados:>4}  mas lejano: {lejano.etiqueta()}")
    if alcanzados < g.numeroNodos():
        print(f"  {'':<20} ({g.numeroNodos() - alcanzados} nodos no alcanzables: "
              f"el grafo no es conexo)")
    return arbol


for N in TAMANOS:
    print(f"\n=== N = {N}  (fuente s = nodo_{FUENTE}) ===")

    filas, cols = dimensionesMalla(N)
    #procesar(f"Malla_{filas}x{cols}", grafoMalla(filas, cols), N)
    #procesar("ErdosRenyi", grafoErdosRenyi(N, 2 * N), N)
    procesar("Gilbert", grafoGilbert(N, min(0.1, 4 / N)), N)
    #procesar("Geografico", grafoGeografico(N, 0.3 if N <= 50 else 0.2), N)
    #procesar("BarabasiAlbert", grafoBarabasiAlbert(N, 3), N)
    #arbol = procesar("DorogovtsevMendes", grafoDorogovtsevMendes(N), N)

# Muestra de etiquetas del ultimo arbol calculado
print("\nEjemplo de nodos del ultimo arbol (Dorogovtsev-Mendes, N=150):")
for nodo in list(arbol.nodos.values())[:8]:
    print("  ", nodo.etiqueta())

print(f"\nArchivos .dot guardados en: {CARPETA_GEN}  y  {CARPETA_DIJ}")