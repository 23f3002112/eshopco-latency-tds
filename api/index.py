import json
from http.server import BaseHTTPRequestHandler

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

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

def percentile(data, p):
    s = sorted(data)
    n = len(s)
    idx = (p / 100) * (n - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= n:
        return s[lo]
    return s[lo] + (idx - lo) * (s[hi] - s[lo])

def compute(regions, threshold_ms):
    result = {}
    for region in regions:
        records = [r for r in DATA if r["region"] == region]
        if not records:
            continue
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]
        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 4),
            "p95_latency": round(percentile(latencies, 95), 4),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 4),
            "breaches": sum(1 for l in latencies if l > threshold_ms),
        }
    return result

class handler(BaseHTTPRequestHandler):
    def _send(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self._send(200, {})

    def do_GET(self):
        self._send(200, {"status": "ok", "endpoint": "POST /api/latency"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            regions = body["regions"]
            threshold_ms = float(body["threshold_ms"])
            self._send(200, compute(regions, threshold_ms))
        except Exception as e:
            self._send(400, {"error": str(e)})
