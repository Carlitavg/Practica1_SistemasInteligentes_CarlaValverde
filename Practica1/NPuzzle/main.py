import argparse
from time import perf_counter

from NPuzzle.tablero import Tablero, mezclar_aleatorio
from NPuzzle.heuristicas import HEURISTICAS
from NPuzzle.agente_npuzzle import AgenteNPuzzle

def imprimir_tablero(t: Tablero):
    N = t.N
    w = len(str(N*N-1))
    for r in range(N):
        fila = t.fichas[r*N:(r+1)*N]
        print(" ".join(("·" if x == 0 else str(x)).rjust(w) for x in fila))
    print()

def parsear_estado(txt: str, N: int) -> Tablero:
    """
    Formato esperado (con o sin comas/espacios):
      '1 2 3 4 5 6 7 8 0'   (N=3)
      '1,2,3,4,5,6,7,8,0'
    """
    tokens = [int(x) for x in txt.replace(",", " ").split()]
    esperado = N*N
    if len(tokens) != esperado or set(tokens) != set(range(esperado)):
        raise ValueError(f"Estado inválido. Debe contener 0..{esperado-1}.")
    return Tablero(N, tuple(tokens))

def main():
    parser = argparse.ArgumentParser(
        description="Resolver N-Puzzle con A* o Codicioso usando heurísticas clásicas."
    )
    parser.add_argument("--N", type=int, default=3, help="Tamaño (3=8-puzzle, 4=15-puzzle).")
    parser.add_argument("--tecnica", choices=["astar", "codicioso"], default="astar")
    parser.add_argument("--heuristica", choices=["fuera", "manhattan", "conflicto"], default="manhattan")
    parser.add_argument("--mezcla", type=int, default=30, help="Número de pasos aleatorios desde la meta.")
    parser.add_argument("--semilla", type=int, default=7, help="Semilla para la mezcla.")
    parser.add_argument(
        "--estado",
        type=str,
        default="",
        help="Estado inicial explícito (ej: '1 2 3 4 5 6 7 8 0'). Si se omite, se usa mezcla aleatoria.",
    )
    parser.add_argument("--mostrar_ruta", action="store_true", help="Imprime todos los tableros de la ruta.")
    args = parser.parse_args()

    # Meta (orden natural con 0 como blanco al final)
    meta = Tablero(args.N, tuple([*range(1, args.N*args.N), 0]))

    # Estado inicial
    if args.estado:
        inicial = parsear_estado(args.estado, args.N)
    else:
        inicial = mezclar_aleatorio(args.N, pasos=args.mezcla, semilla=args.semilla)

    # Heurística
    hfun = HEURISTICAS[args.heuristica]

    # Agente
    agente = AgenteNPuzzle(N=args.N, heuristica=hfun, tecnica=args.tecnica)
    agente.fijar_estados(inicial, meta)

    print("\n== N-Puzzle ==")
    print(f"Técnica: {args.tecnica} | Heurística: {args.heuristica}")
    print("Inicial:")
    imprimir_tablero(inicial)
    print("Meta:")
    imprimir_tablero(meta)

    t0 = perf_counter()
    agente.programa()
    dt = perf_counter() - t0

    ruta = agente.get_acciones()
    metr = (agente.get_medida_rendimiento()
            if hasattr(agente, "get_medida_rendimiento") else
            getattr(agente, "_medida_rendimiento", {}))

    if not ruta:
        print("No se encontró solución.")
        return

    pasos = metr.get("pasos", len(ruta)-1)
    nodos = metr.get("operaciones", "¿?")
    costo = metr.get("costo", pasos)

    print(f"¡Solución encontrada!")
    print(f"Pasos (profundidad): {pasos}")
    print(f"Nodos explorados:    {nodos}")
    print(f"Costo (g):           {costo}")
    print(f"Tiempo:              {dt*1000:.1f} ms")

    if args.mostrar_ruta:
        print("\n--- Ruta ---")
        for i, t in enumerate(ruta):
            print(f"Paso {i}:")
            imprimir_tablero(t)

if __name__ == "__main__":
    main()
