import sys, time, json
from multiprocessing import Process, Queue


def queue_worker(out_queue, items_per_worker):
    for i in range(items_per_worker):
        # Pathological pattern: every single iteration crosses an IPC boundary
        out_queue.put(i % 7)


def run_queue_benchmark(p, total_items=400_000):
    q = Queue()
    items_per_worker = total_items // p
    total_items = items_per_worker * p  # avoid hanging if not divisible
    workers = [Process(target=queue_worker, args=(q, items_per_worker)) for _ in range(p)]
    t0 = time.perf_counter()
    for w in workers:
        w.start()
    collected = 0
    while collected < total_items:  # master consumes everything
        _ = q.get()
        collected += 1
    for w in workers:
        w.join()
    return time.perf_counter() - t0


if __name__ == "__main__":
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 400_000
    cores = [1, 2, 4, 8]
    runtimes = {p: run_queue_benchmark(p, total) for p in cores}
    t1 = runtimes[1]
    print("\n--- Queue Contention Karp-Flatt Analysis ---")
    print(f"P= 1 | Time={t1:6.3f}s")
    for p in [2, 4, 8]:
        tp = runtimes[p]
        sp = t1 / tp
        e = ((p * tp / t1) - 1.0) / (p - 1.0)
        print(f"P={p:2d} | Time={tp:6.3f}s | Speedup={sp:5.2f}x | Karp-Flatt e={e:6.3f}")
    json.dump({str(p): t for p, t in runtimes.items()}, open("results_b.json", "w"), indent=2)