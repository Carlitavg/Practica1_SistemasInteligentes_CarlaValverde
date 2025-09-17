from .tablero import Tablero

def h_fuera_de_lugar(t: Tablero) -> int:
    meta = [*range(1, t.N*t.N), 0]
    return sum(1 for i, f in enumerate(t.fichas) if f and f != meta[i])

def h_manhattan(t: Tablero) -> int:
    return sum(t.manhattan_de_ficha(f) for f in t.fichas if f)

def h_conflicto_lineal(t: Tablero) -> int:
    N = t.N
    man = h_manhattan(t)
    cl = 0
    # filas
    for r in range(N):
        fila = [t.fichas[r*N+c] for c in range(N)]
        cols_meta = [(f-1)%N for f in fila if f and (f-1)//N == r]
        for i in range(len(cols_meta)):
            for j in range(i+1, len(cols_meta)):
                cl += cols_meta[i] > cols_meta[j]
    # columnas
    for c in range(N):
        col = [t.fichas[r*N+c] for r in range(N)]
        filas_meta = [(f-1)//N for f in col if f and (f-1)%N == c]
        for i in range(len(filas_meta)):
            for j in range(i+1, len(filas_meta)):
                cl += filas_meta[i] > filas_meta[j]
    return man + 2*cl

HEURISTICAS = {
    "fuera": h_fuera_de_lugar,
    "manhattan": h_manhattan,
    "conflicto": h_conflicto_lineal,
}
