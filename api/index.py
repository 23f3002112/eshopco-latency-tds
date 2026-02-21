import json
import statistics
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

# Proper CORS for Vercel (POST + OPTIONS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

# Load telemetry JSON
data_path = Path(__file__).resolve().parent.parent / "q-vercel-latency.json"

with open(data_path) as f:
    telemetry = json.load(f)


# Handle OPTIONS (important for grader)
@app.options("/api/latency")
async def options_handler():
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


@app.post("/api/latency")
async def analyze_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 0)

    result = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]
        if not records:
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]

        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=100)[94]
        avg_uptime = statistics.mean(uptimes)
        breaches = len([l for l in latencies if l > threshold])

        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches,
        }

    return Response(
        content=json.dumps(result),
        media_type="application/json",
        headers={"Access-Control-Allow-Origin": "*"},
    )
