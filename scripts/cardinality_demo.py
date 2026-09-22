"""Standalone cardinality-explosion demo for Part E2.

Does NOT touch the real quest-app metrics. Runs its own tiny Prometheus
metrics server on a separate port (9091) so we can point Prometheus at it
temporarily, without affecting the quest-app metrics at all.

Usage:
    python scripts/cardinality_demo.py --with-label     (creates 100 series)
    python scripts/cardinality_demo.py --no-label        (creates 1 series)
"""
import argparse
import time
import uuid
from prometheus_client import Counter, start_http_server

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-label", action="store_true",
                         help="Attach a unique request_id label per call (BAD practice)")
    parser.add_argument("--no-label", action="store_true",
                         help="No request_id label at all (GOOD practice)")
    parser.add_argument("--count", type=int, default=100,
                         help="How many requests to simulate")
    parser.add_argument("--port", type=int, default=9091)
    args = parser.parse_args()

    if args.with_label:
        # BAD: request_id as a label creates one new time series PER unique ID.
        demo_requests_total = Counter(
            "demo_requests_total",
            "Demo counter WITH a per-request unique label (cardinality explosion example)",
            ["request_id"]
        )
    else:
        # GOOD: no unique-valued label, always the same one time series.
        demo_requests_total = Counter(
            "demo_requests_total",
            "Demo counter with NO unique label (normal, low-cardinality example)"
        )

    start_http_server(args.port)
    print(f"Serving metrics on http://localhost:{args.port}/metrics")
    print(f"Simulating {args.count} requests, with_label={args.with_label}")

    for i in range(args.count):
        if args.with_label:
            request_id = uuid.uuid4().hex[:12]
            demo_requests_total.labels(request_id=request_id).inc()
        else:
            demo_requests_total.inc()
        if (i + 1) % 20 == 0:
            print(f"  {i + 1}/{args.count} requests simulated")

    print("Done generating requests. Leaving the metrics server running so")
    print("Prometheus can scrape it — press Ctrl+C to stop.")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()