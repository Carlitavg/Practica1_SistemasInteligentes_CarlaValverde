from typing import Callable, List, Any
from AgenteIA.AgenteBuscador import AgenteBuscador
from .tablero import Tablero

class AgenteNPuzzle(AgenteBuscador):
    def __init__(self, N: int, heuristica: Callable[[Tablero], int], tecnica: str):
        super().__init__()
        self.N = N
        self.heuristica = heuristica
        self._expandidos = 0
        self._modo = (tecnica or "").lower()
        base_tecnica = 'costouniforme' if self._modo in ('astar', 'codicioso') else (self._modo or 'costouniforme')
        if hasattr(self, 'set_tecnica'):
            self.set_tecnica(base_tecnica)
        else:
            try:
                self.tecnica = base_tecnica
            except Exception:
                pass
        self._cache_succ: dict[Tablero, List[Tablero]] = {}
        if hasattr(self, 'add_funcion'):
            self.add_funcion(self._sucesores)
        elif hasattr(self, 'add_funcion_sucesor'):
            self.add_funcion_sucesor(self._sucesores)
        else:
            if hasattr(self, '_AgenteBuscador__funcion_sucesor'):
                getattr(self, '_AgenteBuscador__funcion_sucesor').append(self._sucesores)
            elif hasattr(self, 'funcion_sucesor'):
                fs = getattr(self, 'funcion_sucesor')
                if isinstance(fs, list):
                    fs.append(self._sucesores)

    def fijar_estados(self, inicial: Tablero, meta: Tablero) -> None:
        if hasattr(self, 'set_estado_inicial'): self.set_estado_inicial(inicial)
        else: self.estado_inicial = inicial
        if hasattr(self, 'set_estado_meta'): self.set_estado_meta(meta)
        else: self.estado_meta = meta
        self._expandidos = 0

    def _sucesores(self, t: Tablero) -> List[Tablero]:
        if t in self._cache_succ: return self._cache_succ[t]
        xs = list(t.sucesores())
        self._cache_succ[t] = xs
        self._expandidos += 1
        return xs

    def generar_hijos(self, estado): return self._sucesores(estado)
    def get_hijos(self, estado):     return self._sucesores(estado)

    def get_costo(self, camino: List[Tablero]) -> int:
        g = len(camino) - 1
        estado = camino[-1]
        if self._modo == 'astar': return g + self.heuristica(estado)
        if self._modo == 'codicioso': return self.heuristica(estado)
        return g

    def get_heuristica(self, obj: Any) -> int:
        nodo = obj[-1] if isinstance(obj, list) and obj else obj
        return self.heuristica(nodo)

    def get_acciones(self):
        if hasattr(self, "acciones"):
            return self.acciones
        return None

    def get_medida_rendimiento(self):
        if hasattr(self, "_medida_rendimiento"):
            m = dict(self._medida_rendimiento)
        elif hasattr(self, "medida"):
            m = dict(self.medida)
        else:
            acciones = self.get_acciones()
            pasos = (len(acciones) - 1) if acciones else 0
            m = {"pasos": pasos, "costo": pasos, "operaciones": 0}
        m["operaciones"] = max(int(m.get("operaciones", 0)), int(getattr(self, "_expandidos", 0)))
        return m
