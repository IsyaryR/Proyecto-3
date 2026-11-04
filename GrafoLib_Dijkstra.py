import random
import math
import heapq


class Nodo:
    def __init__(self, id, distancia=None):
        self.id = id #identificador unico 
        self.distancia = distancia #distancia al nodo fuente (la llena Dijkstra)

    def nombre(self): #nombre del nodo en el archivo .dot -> nodo_2
        return f"nodo_{self.id}"

    def etiqueta(self): #texto visible del nodo -> "nodo_2" o "nodo_2 (22.45)"
        if self.distancia is None:
            return self.nombre()
        if math.isinf(self.distancia):
            return f"{self.nombre()} (inf)"
        return f"{self.nombre()} ({self.distancia:.2f})"

    def __repr__(self): #Para imprimir en consola
        return f"Nodo(id={self.id})" #Nodo(id=1)

    def __eq__(self, other): #definicion de nodos iguales si son la misma id
        return isinstance(other, Nodo) and self.id == other.id

    def __hash__(self): #Para ser hashable en diccionario
        return hash(self.id)


class Arista:
    def __init__(self, u, v, peso=1.0):
        self.u = u  # Nodo origen
        self.v = v  # Nodo destino
        self.peso = peso  # Costo de recorrer la arista (Dijkstra requiere peso >= 0)

    def __repr__(self):
        return f"Arista({self.u.id} -> {self.v.id}, peso={self.peso})" #Arista(0 -> 1, peso=3.5)

    def __eq__(self, other): #definicion de arista igual, si tiene el mismo nodo origen y destino
        if not isinstance(other, Arista):
            return False
        return self.u == other.u and self.v == other.v

    def __hash__(self):
        return hash((self.u, self.v))


class Grafo:
    def __init__(self, dirigido=False):
        self.dirigido = dirigido # si es false A -- B; si es true A -> B no implica B -> A
        self.nodos = {} #diccionario de nodos registrados
        self.aristas = [] #lista con todas las aristas
        self.adyacencia = {}  # Diccionario para guardar vecinos de cada nodo id -> set(id_vecino)
        self.pesos = {}  # Diccionario (id_u, id_v) -> peso de la arista
        self.fuente = None  # id del nodo fuente si el grafo es un arbol de Dijkstra

    def agregarNodo(self, nodo): #Funcion para agregar nodo 
        if nodo.id not in self.nodos:
            self.nodos[nodo.id] = nodo
            self.adyacencia[nodo.id] = set()
        return self.nodos[nodo.id]

    def obtenerNodo(self, id):
        return self.nodos[id]  #Regresa el nodo con el id dado.

    def agregarArista(self, u, v, peso=1.0): #Conecta dos nodos con un peso
        if u.id not in self.nodos:
            self.agregarNodo(u)
        if v.id not in self.nodos:
            self.agregarNodo(v)

        # Evitar aristas duplicadas
        if v.id in self.adyacencia[u.id]:
            return None

        arista = Arista(u, v, peso)
        self.aristas.append(arista)
        self.adyacencia[u.id].add(v.id)
        self.pesos[(u.id, v.id)] = peso
        if not self.dirigido:
            self.adyacencia[v.id].add(u.id)
            self.pesos[(v.id, u.id)] = peso
        return arista

    def peso(self, u_id, v_id): #Regresa el peso de la arista u -> v
        return self.pesos[(u_id, v_id)]

    def asignarPesosAleatorios(self, minimo=1.0, maximo=10.0, decimales=2):
        #Asigna a cada arista un peso aleatorio uniforme en [minimo, maximo]
        if minimo < 0:
            raise ValueError("Dijkstra requiere pesos no negativos (minimo >= 0)")
        for a in self.aristas:
            w = round(random.uniform(minimo, maximo), decimales)
            a.peso = w
            self.pesos[(a.u.id, a.v.id)] = w
            if not self.dirigido:
                self.pesos[(a.v.id, a.u.id)] = w

    def vecinos(self, nodo):#Devuelve la lista de nodos que estan conectados directamente al nodo
        return [self.nodos[i] for i in self.adyacencia[nodo.id]]

    def grado(self, nodo):
        return len(self.adyacencia[nodo.id])

    def numeroNodos(self):
        return len(self.nodos)

    def numeroAristas(self):
        return len(self.aristas)

    # =====================================================
    #  Algoritmo de Dijkstra
    #  Calcula el arbol de caminos mas cortos desde el nodo
    #  fuente s. Regresa un nuevo Grafo donde:
    #   - cada nodo alcanzable guarda su distancia a s
    #   - cada nodo (excepto s) tiene UNA arista que llega
    #     desde su predecesor en el camino mas corto
    #  s puede ser un objeto Nodo o directamente su id.
    # =====================================================
    def Dijkstra(self, s):
        s_id = s.id if isinstance(s, Nodo) else s
        if s_id not in self.nodos:
            raise ValueError(f"El nodo fuente {s_id} no existe en el grafo")

        dist = {i: math.inf for i in self.nodos}  #distancia tentativa a cada nodo
        padre = {i: None for i in self.nodos}     #predecesor en el camino mas corto
        dist[s_id] = 0.0
        visitados = set()                          #nodos con distancia ya definitiva
        cola = [(0.0, s_id)]                       #cola de prioridad (distancia, id)

        while cola:
            d_u, u = heapq.heappop(cola)  #nodo no visitado con menor distancia
            if u in visitados:            #entrada vieja de la cola, se ignora
                continue
            visitados.add(u)

            for v in self.adyacencia[u]:  #relajacion de cada arista u -> v
                w = self.pesos[(u, v)]
                if w < 0:
                    raise ValueError("Dijkstra no admite pesos negativos")
                nueva = d_u + w
                if nueva < dist[v]:
                    dist[v] = nueva
                    padre[v] = u
                    heapq.heappush(cola, (nueva, v))

        #Construccion del arbol de caminos mas cortos (solo nodos alcanzables)
        arbol = Grafo(dirigido=self.dirigido)
        arbol.fuente = s_id
        for i in self.nodos:
            if i in visitados:
                arbol.agregarNodo(Nodo(i, distancia=dist[i]))
        for i in self.nodos:
            if i in visitados and padre[i] is not None:
                arbol.agregarArista(arbol.obtenerNodo(padre[i]),
                                    arbol.obtenerNodo(i),
                                    peso=self.pesos[(padre[i], i)])
        arbol.distancias = dist  #diccionario completo (inf = no alcanzable)
        return arbol

    def _paresPosibles(self): #Devuelve todos los pares (i, j) con i < j sobre los ids actuales.
        ids = list(self.nodos.keys()) #diccionario donde las claves son los nodos [0,1,2,3]
        pares = [] #lista vacia para guardar cada pareja en forma de tupla
        for i in range(len(ids)):
            for j in range(i+1, len(ids)):
                pares.append((ids[i], ids[j]))
        return pares #[(0,1),(0,2),(1,2),...]

    def guardarGraphViz(self, ruta, nombre="Grafo", mostrarPesos=True): #Guarda el grafo en formato DOT (GraphViz).
        tipo = "digraph" if self.dirigido else "graph"
        conector = "->" if self.dirigido else "--"

        lineas = [f'{tipo} {nombre} {{']
        for nodo in self.nodos.values():
            #nombre interno "nodo_2" y etiqueta visible "nodo_2 (22.45)"
            atributos = [f'label="{nodo.etiqueta()}"']
            if nodo.id == self.fuente: #resalta el nodo fuente del arbol
                atributos.append('style=filled')
                atributos.append('fillcolor=lightblue')
            lineas.append(f'    "{nodo.nombre()}" [{", ".join(atributos)}];')
        for a in self.aristas:
            extra = f' [label="{a.peso:g}"]' if mostrarPesos else ""
            lineas.append(f'    "{a.u.nombre()}" {conector} "{a.v.nombre()}"{extra};')
        lineas.append("}")

        with open(ruta, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))
# =========================================================
#  Funciones de generacion de grafos
# =========================================================
#---------------------------------------
#         Grafo de malla m x n.
#  Conecta cada nodo con su vecino de 
#  la derecha y su vecino de abajo
#---------------------------------------
def grafoMalla(m, n, dirigido=False):
    if m<1 or n<1:#Validacion de la malla minimo 1 fila y minimo 1 columna
        raise ValueError("m y n deben ser >= 1")
    g=Grafo(dirigido=dirigido)#instancia vacia 

    for i in range(m): #recorre las filas de 0 a m-1
        for j in range(n):#recorre las columnas de 0 a n-1
            g.agregarNodo(Nodo(i*n+j))

    for i in range(m):
        for j in range(n):
            actual=g.obtenerNodo(i*n+j)
            if i+1 < m: #conexion vertical con el nodo de abajo
                g.agregarArista(actual, g.obtenerNodo((i +1)*n+j))
            if j+1 < n: #conexion horizontal con el nodo de la derecha
                g.agregarArista(actual, g.obtenerNodo(i*n + (j+1)))
    return g
#---------------------------------------------------------
#  Grafo aleatorio Erdos-Renyi con n nodos y m aristas.
# Obtiene las posibles parejas de nodos posibles para conectarse
#---------------------------------------------------------
def grafoErdosRenyi(n, m, dirigido=False):
    if n <= 0: #verifica que numero de nodos n sea mayor a 0
        raise ValueError("n debe ser > 0")
    g = Grafo(dirigido=dirigido)#grafo vacio
    for i in range(n): #crea n nodos ennumerados de 0 a n-1 
        g.agregarNodo(Nodo(i))

    max_aristas = n*(n-1) if dirigido else n*(n-1) // 2 #calculo de aristas unicas maximas en el grafo
    if m > max_aristas:
        raise ValueError(f"m={m} excede el máximo posible de aristas ({max_aristas})")

    pares = g._paresPosibles()#regresa lista con todos los pares (u,v)  u<v
    if dirigido: #si es dirigido, duplica pares por el sentido inverso de cada combinacion
        pares_dir = []
        for (u, v) in pares:
            pares_dir.append((u, v))
            pares_dir.append((v, u))
        pares = pares_dir

    for (u_id, v_id) in random.sample(pares, m):#Elige m elementos de la lista pares sin repeticion y uniforme
        g.agregarArista(g.obtenerNodo(u_id), g.obtenerNodo(v_id))
    return g
#-----------------------------------------------------------
#  Grafo aleatorio Gilbert con cada arista con probabilidad p.
#  Grafo aleatorio basado en probabilidad
#-----------------------------------------------------------
def grafoGilbert(n, p, dirigido=False):
    if n <= 0: #validacion de numeros positivos
        raise ValueError("n debe ser > 0")
    if not (0.0 <= p <= 1.0):#probabilidad entre 0 a 100%
        raise ValueError("p debe estar en [0, 1]")
    g = Grafo(dirigido=dirigido)
    for i in range(n): #crea n nodos iniciales del 0 al n-1
        g.agregarNodo(Nodo(i))

    for (u_id, v_id) in g._paresPosibles():#recorre todas las combinaciones posibles de pares de nodos
        if random.random() < p: #compara el numero decimal general aleatorio con la probabilidad de p
            g.agregarArista(g.obtenerNodo(u_id), g.obtenerNodo(v_id))
        if dirigido and random.random() < p: #segundo lanzamiento para ver si existe arista en sentido contrario
            g.agregarArista(g.obtenerNodo(v_id), g.obtenerNodo(u_id))
    return g
#--------------------------------------------------------------------
#   Grafo geografico: nodos en [0,1]^2, arista si distancia <= r.
# Simula nodos ubicados en un cuadrado de 1 x 1 (Plano 2D)
#--------------------------------------------------------------------
def grafoGeografico(n, r, dirigido=False):
    if n <= 0: #validacion de nodos mayor a 0
        raise ValueError("n debe ser > 0")
    if not (0.0 < r < 1.0):#radio de cobertura dentro de 0 a 1
        raise ValueError("r debe estar en (0, 1)")
    g = Grafo(dirigido=dirigido)
    coords = [] #lista de coordenadas para guardar la posicion de cada nodo
    for i in range(n): #posicionamiento de nodos
        coords.append((random.random(), random.random()))#para cada nodo asigna una coordenada aleatoria
        g.agregarNodo(Nodo(i)) #añade tupla a lista de coords y registra nodo(i) en grafo

    for i in range(n):
        for j in range(i+1, n):
            xi, yi = coords[i] #extrae coordenadas de nodo i
            xj, yj = coords[j] #extrae coordenadas de nodo j
            if math.hypot(xi-xj, yi-yj) <= r: #teorema de pitagoras para distancia euclidiana, si  la distancia es >= r crea la arista
                g.agregarArista(g.obtenerNodo(i), g.obtenerNodo(j))
                if dirigido:# si es dirigido añade la arista en sentido inverso
                    g.agregarArista(g.obtenerNodo(j), g.obtenerNodo(i))
    return g
#---------------------------------------------------------
#           Grafo aleatorio Barabasi-Albert.
#---------------------------------------------------------
def grafoBarabasiAlbert(n, d, dirigido=False):
    if n <= 0:#Validacion
        raise ValueError("n debe ser > 0")
    if d < 1:
        raise ValueError("d debe ser >= 1")
    if d >= n:# inicializacion
        d = n - 1

    g = Grafo(dirigido=dirigido)
    for i in range(n):
        g.agregarNodo(Nodo(i))

    iniciales = min(d+1, n)# crea iniciales con d+1
    for i in range(iniciales):
        for j in range(i+1, iniciales):
            g.agregarArista(g.obtenerNodo(i), g.obtenerNodo(j))

    for nuevo in range(iniciales, n):#para cada nodo que ingresa 
        existentes = list(range(nuevo))#lista de id de nodos que forman parte dle grafo
        grados = [max(g.grado(g.obtenerNodo(k)), 1) for k in existentes]#cuantas conexiones tiene cada nodo

        seleccionados = set() #se usa set() y while para garantizar que el nuevo nodo eliga d vecinos diferentes sin duplicar conexiones
        while len(seleccionados) < d and len(seleccionados) < len(existentes):
            elegido = random.choices(existentes, weights=grados, k=1)[0]
            seleccionados.add(elegido)

        for objetivo in seleccionados:#crea d aristas entre el nodo nuevo y cada nodo objetivo elegido
            g.agregarArista(g.obtenerNodo(nuevo), g.obtenerNodo(objetivo))
            if dirigido:
                g.agregarArista(g.obtenerNodo(objetivo), g.obtenerNodo(nuevo))
    return g
#---------------------------------------------------------
#        Grafo aleatorio Dorogovtsev-Mendes.
#---------------------------------------------------------
def grafoDorogovtsevMendes(n, dirigido=False):
    if n<3:# requiere 3 nodos minimo para el triangulo
        raise ValueError("n debe ser >= 3")
    g = Grafo(dirigido=dirigido)
    for i in range(3): #crea la estructura del grafo con 3 nodos(0,1,2)
        g.agregarNodo(Nodo(i))
    #conecta los nodos 0,1 y 2 para formar triangulo
    g.agregarArista(g.obtenerNodo(0), g.obtenerNodo(1))
    g.agregarArista(g.obtenerNodo(1), g.obtenerNodo(2))
    g.agregarArista(g.obtenerNodo(2), g.obtenerNodo(0))
    #Para cada nuevo nodo desde 3 a n-1
    for nuevo in range(3, n):
        g.agregarNodo(Nodo(nuevo))#registra nodo nuevo
        arista = random.choice(g.aristas)#elige una arista al azar 
        u, v = arista.u, arista.v #extrae extremos de u y v
        #conecta nodo nuevo con u y v para formar nuevo triangulo
        g.agregarArista(g.obtenerNodo(nuevo), g.obtenerNodo(u.id))
        g.agregarArista(g.obtenerNodo(nuevo), g.obtenerNodo(v.id))
        if dirigido:
            g.agregarArista(g.obtenerNodo(u.id), g.obtenerNodo(nuevo))
            g.agregarArista(g.obtenerNodo(v.id), g.obtenerNodo(nuevo))
    return g