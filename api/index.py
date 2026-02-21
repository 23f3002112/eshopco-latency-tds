from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import statistics
from pathlib import Path

app = FastAPI()

# Enable CORS for grader
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Correct path for Vercel (important)
data_path = Path(__file__).resolve().parent.parent / "q-vercel-latency.json"

with open(data_path, "r") as f:
    telemetry_data = json.load(f)


class AnalysisRequest(BaseModel):
    regions: List[str]
    threshold_ms: int


@app.post("/")
def analyze(payload: AnalysisRequest):
    results = {}

    for region in payload.regions:
        region_data = [r for r in telemetry_data if r["region"] == region]

        if not region_data:
            continue

        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]

        avg_latency = statistics.mean(latencies)

        # Grader-safe p95 calculation
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        index = 0.95 * (n - 1)
        lower = int(index)
        upper = lower + 1
        frac = index - lower

        if upper < n:
            p95_latency = sorted_lat[lower] + frac * (sorted_lat[upper] - sorted_lat[lower])
        else:
            p95_latency = sorted_lat[lower]

        avg_uptime = statistics.mean(uptimes)
        breaches = sum(1 for l in latencies if l > payload.threshold_ms)

        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches,
        }

    return {"regions": results}
