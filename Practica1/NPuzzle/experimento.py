from time import perf_counter
from statistics import mean
import argparse, sys

from .tablero import Tablero, mezclar_aleatorio, es_resoluble
from .heuristicas import HEURISTICAS
from .agente_npuzzle import AgenteNPuzzle

def factor_ramificacion_efectivo(nodos: int, profundidad: int) -> float:
    if profundidad <= 0: return 0.0
    lo, hi = 1.000001, 10.0
    for _ in range(60):
        mid = (lo+hi)/2
        total, pot = 1.0, 1.0
        for _ in range(profundidad):
            pot *= mid; total += pot
            if total > nodos + 1: break
        if total > nodos + 1: hi = mid
        else: lo = mid
    return (lo+hi)/2

def ejecutar_solvedor(N: int, pasos_mezcla: int, tecnica: str, nombre_h: str,
                      k: int, semilla: int):
    meta = Tablero(N, tuple([*range(1, N*N), 0]))
    hfun = HEURISTICAS[nombre_h]
    pasos, tiempos, nodos, fallas = [], [], [], 0

    for i in range(k):
        s = mezclar_aleatorio(N, pasos=pasos_mezcla, semilla=semilla+i)
        if not es_resoluble(s): 
            s = mezclar_aleatorio(N, pasos=pasos_mezcla+1, semilla=semilla+i+999)

        ag = AgenteNPuzzle(N, heuristica=hfun, tecnica=tecnica)
        ag.fijar_estados(s, meta)

        t0 = perf_counter(); ag.programa(); dt = perf_counter() - t0

        acc = ag.get_acciones()
        metr = ag.get_medida_rendimiento()

        if acc and s != meta and metr:
            pasos.append(metr.get("pasos", len(acc)-1))
            tiempos.append(dt)
            nodos.append(metr.get("operaciones", 0))
        else:
            fallas += 1

        if (i+1) % max(1, k//10) == 0:
            print(f"  [{tecnica}/{nombre_h}] {i+1}/{k} instancias...", flush=True)

    p = mean(pasos) if pasos else float("inf")
    t = mean(tiempos) if tiempos else float("inf")
    n = mean(nodos) if nodos else float("inf")
    b = factor_ramificacion_efectivo(int(n), int(p)) if pasos else float("inf")
    return {"tecnica": tecnica, "heuristica": nombre_h, "pasos": p,
            "tiempo_s": t, "nodos": n, "b*": b, "incompletos": fallas}

def main():
    parser = argparse.ArgumentParser(description="Experimentos N-Puzzle (Greedy/A* × heurísticas).")
    parser.add_argument("--N", type=int, default=3)
    parser.add_argument("--mezcla", type=int, default=40)
    parser.add_argument("--k", type=int, default=100, help="Cantidad de instancias por combo (sug: 100 al probar)")
    parser.add_argument("--semilla", type=int, default=7)
    parser.add_argument("--tecnicas", type=str, default="codicioso,astar",
                        help="Lista separada por comas (opciones: codicioso,astar)")
    parser.add_argument("--heuristicas", type=str, default="fuera,manhattan,conflicto",
                        help="Lista separada por comas (fuera, manhattan, conflicto)")
    args = parser.parse_args()

    tecnicas = [t.strip() for t in args.tecnicas.split(",") if t.strip()]
    heuristicas = [h.strip() for h in args.heuristicas.split(",") if h.strip()]

    print("=== RESUMEN ===", flush=True)
    if not tecnicas or not heuristicas:
        print("No hay configuraciones. Revisa --tecnicas y --heuristicas.", flush=True)
        sys.exit(1)

    for tec in tecnicas:
        for h in heuristicas:
            if h not in HEURISTICAS:
                print(f"  [SKIP] Heurística desconocida: {h}", flush=True)
                continue
            print(f"\n> Ejecutando {tec} × {h}  (N={args.N}, mezcla={args.mezcla}, k={args.k})", flush=True)
            try:
                r = ejecutar_solvedor(args.N, args.mezcla, tec, h, k=args.k, semilla=args.semilla)
                print(f"{r['tecnica']:10s} | {r['heuristica']:10s} | "
                      f"pasos={r['pasos']:.2f} | t={r['tiempo_s']*1000:.1f} ms | "
                      f"nodos={r['nodos']:.1f} | b*={r['b*']:.3f} | incompletos={r['incompletos']}",
                      flush=True)
            except Exception as e:
                print(f"  [ERROR] {tec} × {h}: {e}", flush=True)

if __name__ == "__main__":
    main()
