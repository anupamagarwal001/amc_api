from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional

API_KEY = "my-secret-key"   # change this to something secure later

app = FastAPI(title="AMC Tools API")

# --- Data models ---
class DataPoint(BaseModel):
    year: int
    value: float

class YoYRequest(BaseModel):
    data_series: List[DataPoint]

class Delta(BaseModel):
    year: int
    current: float
    previous: float
    abs_change: float
    pct_change: Optional[float]

class YoYResponse(BaseModel):
    sorted_series: List[DataPoint]
    deltas: List[Delta]
    notes: List[str] = []

# --- Main endpoint ---
@app.post("/compute_yoy_deltas", response_model=YoYResponse)
def compute_yoy_deltas(req: YoYRequest, x_api_key: str = Header(None, convert_underscores=False)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    series = sorted(req.data_series, key=lambda d: d.year)
    deltas = []
    notes = []

    for i in range(1, len(series)):
        cur, prev = series[i], series[i - 1]
        if prev.value == 0:
            pct = None
            notes.append(f"Previous value zero for {prev.year}")
        else:
            pct = round((cur.value - prev.value) / prev.value * 100, 2)
        deltas.append({
            "year": cur.year,
            "current": cur.value,
            "previous": prev.value,
            "abs_change": round(cur.value - prev.value, 2),
            "pct_change": pct
        })
    return {"sorted_series": series, "deltas": deltas, "notes": notes}
