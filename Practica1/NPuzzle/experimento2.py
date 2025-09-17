from time import perf_counter
from statistics import mean
import argparse, csv, sys

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
    filas = []

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
            p = metr.get("pasos", len(acc)-1)
            n = metr.get("operaciones", 0)
            t = dt
            pasos.append(p); tiempos.append(t); nodos.append(n)
            filas.append({
                "instancia": i,
                "tecnica": tecnica,
                "heuristica": nombre_h,
                "N": N,
                "mezcla": pasos_mezcla,
                "pasos": p,
                "tiempo_s": t,
                "nodos": n
            })
        else:
            fallas += 1

        if (i+1) % max(1, k//10) == 0:
            print(f"  [{tecnica}/{nombre_h}] {i+1}/{k} instancias...", flush=True)

    prom_p = mean(pasos) if pasos else float("inf")
    prom_t = mean(tiempos) if tiempos else float("inf")
    prom_n = mean(nodos) if nodos else float("inf")
    b = factor_ramificacion_efectivo(int(prom_n), int(prom_p)) if pasos else float("inf")
    resumen = {"tecnica": tecnica, "heuristica": nombre_h, "pasos": prom_p,
               "tiempo_s": prom_t, "nodos": prom_n, "b*": b, "incompletos": fallas}
    return resumen, filas

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--N", type=int, default=3)
    parser.add_argument("--mezcla", type=int, default=40)
    parser.add_argument("--k", type=int, default=1000)
    parser.add_argument("--semilla", type=int, default=7)
    parser.add_argument("--out", type=str, default="resultados_npuzzle.csv")
    parser.add_argument("--tecnicas", type=str, default="codicioso,astar")
    parser.add_argument("--heuristicas", type=str, default="fuera,manhattan,conflicto")
    args = parser.parse_args()

    tecnicas = [t.strip() for t in args.tecnicas.split(",") if t.strip()]
    heuristicas = [h.strip() for h in args.heuristicas.split(",") if h.strip()]

    print("=== RESUMEN ===", flush=True)

    todos = []
    for tec in tecnicas:
        for h in heuristicas:
            if h not in HEURISTICAS:
                print(f"[SKIP] Heurística desconocida: {h}", flush=True)
                continue
            print(f"\n> Ejecutando {tec} × {h}  (N={args.N}, mezcla={args.mezcla}, k={args.k})", flush=True)
            r, filas = ejecutar_solvedor(args.N, args.mezcla, tec, h, k=args.k, semilla=args.semilla)
            print(f"{r['tecnica']:10s} | {r['heuristica']:10s} | pasos={r['pasos']:.2f} | "
                  f"t={r['tiempo_s']*1000:.1f} ms | nodos={r['nodos']:.1f} | b*={r['b*']:.3f} | "
                  f"incompletos={r['incompletos']}", flush=True)
            todos.extend(filas)

    if todos:
        with open(args.out, "w", newline="") as f:
            campos = ["instancia","tecnica","heuristica","N","mezcla","pasos","tiempo_s","nodos"]
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader(); w.writerows(todos)
        print(f"\nCSV -> {args.out}", flush=True)
    else:
        print("\nSin filas para escribir CSV.", flush=True)

if __name__ == "__main__":
    main()
