from dataclasses import dataclass
from typing import Tuple, Iterable, List
import random



@dataclass(frozen=True, order=True)

class Tablero:
    N: int
    fichas: Tuple[int, ...]  # 0 = blanco

    def posicion(self, ficha: int) -> tuple[int, int]:
        i = self.fichas.index(ficha)
        return divmod(i, self.N)

    def es_meta(self) -> bool:
        return self.fichas == tuple([*range(1, self.N*self.N), 0])

    def sucesores(self) -> Iterable["Tablero"]:
        N = self.N
        r0, c0 = self.posicion(0)
        for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
            nr, nc = r0+dr, c0+dc
            if 0 <= nr < N and 0 <= nc < N:
                j0, j1 = r0*N+c0, nr*N+nc
                t = list(self.fichas)
                t[j0], t[j1] = t[j1], t[j0]
                yield Tablero(N, tuple(t))

    def manhattan_de_ficha(self, ficha: int) -> int:
        if ficha == 0: return 0
        N = self.N
        r, c = self.posicion(ficha)
        gr, gc = divmod(ficha-1, N)
        return abs(r-gr) + abs(c-gc)

def contar_inversiones(a: List[int]) -> int:
    a = [x for x in a if x != 0]
    inv = 0
    for i in range(len(a)):
        for j in range(i+1, len(a)):
            inv += a[i] > a[j]
    return inv

def es_resoluble(t: Tablero) -> bool:
    N = t.N
    inv = contar_inversiones(list(t.fichas))
    if N % 2 == 1:
        return inv % 2 == 0
    r0, _ = t.posicion(0)
    fila_desde_abajo = N - r0
    return (inv + fila_desde_abajo) % 2 == 1

def mezclar_aleatorio(N: int, pasos: int = 40, semilla: int | None = None) -> Tablero:
    if semilla is not None: random.seed(semilla)
    t = Tablero(N, tuple([*range(1, N*N), 0]))
    anterior = None
    for _ in range(pasos):
        cands = list(t.sucesores())
        if anterior is not None:
            cands = [x for x in cands if x.fichas != anterior]
        nxt = random.choice(cands)
        anterior = t.fichas
        t = nxt
    return t
