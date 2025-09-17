import time
import heapq
from AgenteIA.Agente import Agente

class AgenteBuscador(Agente):
    def __init__(self):
        super().__init__()
        self.estado_inicial = None
        self.estado_meta = None
        self.funcion_sucesor = []  # lista de callables: succ(nodo) -> list[str] | str | None
        self.tecnica = None        # 'anchura'|'profundidad'|'costouniforme'|'codicioso'|'astar'

    def add_funcion_sucesor(self, fun):
        self.funcion_sucesor.append(fun)

    def get_hijos(self, nodo):
        """Acepta funciones sucesor que devuelven un hijo, lista de hijos o None."""
        hijos = []
        for fun in self.funcion_sucesor:
            h = fun(nodo)
            if h is None:
                continue
            if isinstance(h, (list, tuple, set)):
                hijos.extend(h)
            else:
                hijos.append(h)
        return hijos

    @staticmethod
    def medir_tiempo(funcion):
        def _wrapper(*args, **kwards):
            inicio = time.time()
            c = funcion(*args, **kwards)
            print("Tiempo de ejecucion: ", time.time() - inicio)
            return c
        return _wrapper

    def get_costo(self, camino):
        """Debe retornar g(c) = costo real acumulado del CAMINO."""
        raise Exception("Error: No existe implementacion de get_costo(camino)")

    def get_heuristica(self, nodo):
        """Debe retornar h(nodo) (no de todo el camino)."""
        raise Exception("Error: No existe implementacion de get_heuristica(nodo)")

    def test_objetivo(self, e):
        return e == self.estado_meta

    def programa(self):
        # Soporte BFS/DFS y ordenamientos por clave externa
        if self.tecnica in ('anchura', 'profundidad'):
            frontera = [[self.estado_inicial]]
            visitados = set([self.estado_inicial])
            while frontera:
                camino = frontera.pop() if self.tecnica == 'profundidad' else frontera.pop(0)
                nodo = camino[-1]

                if self.test_objetivo(nodo):
                    self.acciones = camino
                    break

                for hijo in self.get_hijos(nodo):
                    if hijo in visitados:
                        continue
                    if hijo in camino:   # evita ciclos en el mismo camino
                        continue
                    visitados.add(hijo)
                    nuevo = camino + [hijo]
                    frontera.append(nuevo)

        elif self.tecnica in ('costouniforme', 'codicioso', 'astar'):
            # Usamos una priority queue sobre caminos completos
            # clave:
            #  - UCS: f = g(camino)
            #  - Greedy: f = h(ultimo)
            #  - A*: f = g(camino) + h(ultimo)
            def clave(camino):
                ultimo = camino[-1]
                if self.tecnica == 'costouniforme':
                    return self.get_costo(camino)
                elif self.tecnica == 'codicioso':
                    return self.get_heuristica(ultimo)
                else:  # 'astar'
                    return self.get_costo(camino) + self.get_heuristica(ultimo)

            pq = []
            heapq.heappush(pq, (0, [self.estado_inicial]))
            # Para evitar reexpandir estados con peor g, llevamos best_g por nodo (A*/UCS)
            best_g = {self.estado_inicial: 0}

            while pq:
                _, camino = heapq.heappop(pq)
                nodo = camino[-1]

                if self.test_objetivo(nodo):
                    self.acciones = camino
                    break

                g_actual = self.get_costo(camino)

                for hijo in self.get_hijos(nodo):
                    if hijo in camino:  # evita ciclos
                        continue
                    nuevo = camino + [hijo]
                    g_nuevo = self.get_costo(nuevo)

                    if self.tecnica in ('costouniforme', 'astar'):
                        # Relaxation estilo Dijkstra/A*: solo si mejora g del ultimo
                        if hijo not in best_g or g_nuevo < best_g[hijo]:
                            best_g[hijo] = g_nuevo
                            heapq.heappush(pq, (clave(nuevo), nuevo))
                    else:
                        # Greedy ignora g, solo h
                        heapq.heappush(pq, (clave(nuevo), nuevo))
        else:
            raise ValueError(f"Técnica no soportada: {self.tecnica}")
