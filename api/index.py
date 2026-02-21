from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA = [
  {"region":"apac","service":"payments","latency_ms":187.76,"uptime_pct":97.631},
  {"region":"apac","service":"support","latency_ms":219.83,"uptime_pct":98.052},
  {"region":"apac","service":"catalog","latency_ms":127.16,"uptime_pct":97.886},
  {"region":"apac","service":"checkout","latency_ms":188.11,"uptime_pct":98.196},
  {"region":"apac","service":"checkout","latency_ms":125.29,"uptime_pct":97.596},
  {"region":"apac","service":"catalog","latency_ms":134.24,"uptime_pct":99.325},
  {"region":"apac","service":"recommendations","latency_ms":196.49,"uptime_pct":98.763},
  {"region":"apac","service":"checkout","latency_ms":129.34,"uptime_pct":97.161},
  {"region":"apac","service":"recommendations","latency_ms":159.63,"uptime_pct":98.042},
  {"region":"apac","service":"support","latency_ms":205.29,"uptime_pct":98.13},
  {"region":"apac","service":"payments","latency_ms":232.07,"uptime_pct":98.654},
  {"region":"apac","service":"payments","latency_ms":218.52,"uptime_pct":98.362},
  {"region":"emea","service":"recommendations","latency_ms":110.34,"uptime_pct":98.174},
  {"region":"emea","service":"checkout","latency_ms":234.27,"uptime_pct":99.442},
  {"region":"emea","service":"checkout","latency_ms":116.35,"uptime_pct":98.682},
  {"region":"emea","service":"recommendations","latency_ms":225.72,"uptime_pct":97.365},
  {"region":"emea","service":"catalog","latency_ms":134.63,"uptime_pct":97.698},
  {"region":"emea","service":"support","latency_ms":230.52,"uptime_pct":97.484},
  {"region":"emea","service":"support","latency_ms":212.93,"uptime_pct":97.968},
  {"region":"emea","service":"support","latency_ms":157.21,"uptime_pct":98.73},
  {"region":"emea","service":"payments","latency_ms":178.1,"uptime_pct":98.61},
  {"region":"emea","service":"catalog","latency_ms":179.63,"uptime_pct":97.135},
  {"region":"emea","service":"catalog","latency_ms":225.58,"uptime_pct":98.652},
  {"region":"emea","service":"support","latency_ms":204.49,"uptime_pct":99.359},
  {"region":"amer","service":"checkout","latency_ms":146.18,"uptime_pct":97.796},
  {"region":"amer","service":"recommendations","latency_ms":233.91,"uptime_pct":98.571},
  {"region":"amer","service":"payments","latency_ms":165.37,"uptime_pct":98.053},
  {"region":"amer","service":"checkout","latency_ms":218.43,"uptime_pct":97.267},
  {"region":"amer","service":"support","latency_ms":210.55,"uptime_pct":99.286},
  {"region":"amer","service":"checkout","latency_ms":141.76,"uptime_pct":98.591},
  {"region":"amer","service":"support","latency_ms":231.16,"uptime_pct":99.164},
  {"region":"amer","service":"payments","latency_ms":145.87,"uptime_pct":97.444},
  {"region":"amer","service":"checkout","latency_ms":130.03,"uptime_pct":97.143},
  {"region":"amer","service":"support","latency_ms":139.24,"uptime_pct":98.167},
  {"region":"amer","service":"recommendations","latency_ms":156.9,"uptime_pct":98.038},
  {"region":"amer","service":"checkout","latency_ms":168.4,"uptime_pct":97.907},
]

class QueryRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

def percentile(data, p):
    sorted_data = sorted(data)
    n = len(sorted_data)
    idx = (p / 100) * (n - 1)
    lower = int(idx)
    upper = lower + 1
    if upper >= n:
        return sorted_data[lower]
    return sorted_data[lower] + (idx - lower) * (sorted_data[upper] - sorted_data[lower])

def compute(req: QueryRequest):
    result = {}
    for region in req.regions:
        records = [r for r in DATA if r["region"] == region]
        if not records:
            continue
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]
        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 4),
            "p95_latency": round(percentile(latencies, 95), 4),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 4),
            "breaches": sum(1 for l in latencies if l > req.threshold_ms),
        }
    return result

@app.options("/api/latency")
async def options_handler():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/api/latency")
async def check_latency(req: QueryRequest):
    return JSONResponse(
        content=compute(req),
        headers={"Access-Control-Allow-Origin": "*"}
    )

@app.get("/")
async def root():
    return {"status": "ok", "endpoint": "POST /api/latency"}
