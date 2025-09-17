import argparse, csv, math
from collections import defaultdict

def leer_csv(archivo):
    filas = []
    with open(archivo, newline="") as f:
        for row in csv.DictReader(f):
            row["instancia"] = int(row["instancia"])
            row["N"] = int(row["N"])
            row["mezcla"] = int(row["mezcla"])
            row["pasos"] = float(row["pasos"])
            row["tiempo_s"] = float(row["tiempo_s"])
            row["nodos"] = float(row["nodos"])
            filas.append(row)
    return filas

def emparejar(filas, tecnica, h1, h2, metrica):
    by_key = defaultdict(dict)
    for r in filas:
        if r["tecnica"] != tecnica: continue
        key = r["instancia"]
        by_key[key][r["heuristica"]] = r
    x, y = [], []
    for key, d in by_key.items():
        if h1 in d and h2 in d:
            x.append(d[h1][metrica])
            y.append(d[h2][metrica])
    return x, y

def wilcoxon_approx(x, y):
    d = [a - b for a, b in zip(x, y)]
    d = [v for v in d if v != 0]
    n = len(d)
    if n == 0:
        return 0.0, 1.0, 0
    absd = list(map(abs, d))
    idx = list(range(n))
    idx.sort(key=lambda i: absd[i])
    ranks = [0.0]*n
    i = 0
    r = 1
    while i < n:
        j = i
        while j+1 < n and absd[idx[j+1]] == absd[idx[i]]:
            j += 1
        avg = (r + (r + (j - i))) / 2.0
        for k in range(i, j+1):
            ranks[idx[k]] = avg
        r += (j - i + 1)
        i = j + 1
    Wpos = sum(ranks[i] for i in range(n) if d[i] > 0)
    mu = n*(n+1)/4.0
    sigma = math.sqrt(n*(n+1)*(2*n+1)/24.0)
    z = (Wpos - mu) / sigma if sigma > 0 else 0.0
    p = math.erfc(abs(z)/math.sqrt(2))
    return z, p, n

def t_pareada(x, y):
    try:
        import statistics, math
        n = len(x)
        if n == 0: return 0.0, 1.0, 0
        d = [a-b for a,b in zip(x,y)]
        md = sum(d)/n
        sd = statistics.pstdev(d) if n==1 else statistics.stdev(d)
        if sd == 0: return 0.0, 1.0, n
        t = md / (sd / math.sqrt(n))
        try:
            import mpmath as mp
            df = n-1
            p = 2*(1-mp.gammainc((df+1)/2, 0, (abs(t)**2)/ (df))/mp.gamma((df+1)/2))
        except Exception:
            p = 1.0
        return t, float(p), n
    except Exception:
        return 0.0, 1.0, 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archivo", default="resultados_npuzzle.csv")
    ap.add_argument("--tecnica", choices=["codicioso","astar"], required=True)
    ap.add_argument("--h1", choices=["fuera","manhattan","conflicto"], required=True)
    ap.add_argument("--h2", choices=["fuera","manhattan","conflicto"], required=True)
    ap.add_argument("--metrica", choices=["nodos","tiempo_s","pasos"], default="nodos")
    ap.add_argument("--test", choices=["wilcoxon","tpareada"], default="wilcoxon")
    args = ap.parse_args()

    filas = leer_csv(args.archivo)
    x, y = emparejar(filas, args.tecnica, args.h1, args.h2, args.metrica)

    if args.test == "tpareada":
        stat, p, n = t_pareada(x, y)
        print(f"t pareada: t={stat:.4f}, n={n}, p≈{p:.6f}")
    else:
        stat, p, n = wilcoxon_approx(x, y)
        print(f"Wilcoxon (aprox): z≈{stat:.4f}, n={n}, p≈{p:.6f}")

    if p < 0.05:
        print("Diferencia significativa (α=0.05).")
    else:
        print("No significativa (α=0.05).")

if __name__ == "__main__":
    main()
