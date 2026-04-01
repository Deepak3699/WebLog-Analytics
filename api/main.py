import os
import re
import time
import joblib
import hashlib
import pandas as pd

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# -----------------------------------
# INIT APP
# -----------------------------------
app = FastAPI(title="Web Log Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# LOAD MODEL
# -----------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "error_model.pkl")

try:
    bundle = joblib.load(MODEL_PATH)
    model = bundle["model"]
    features = bundle["features"]
    print(f"✅ Model loaded ({len(features)} features)")
except Exception as e:
    raise RuntimeError(f"❌ Model load failed: {e}")

# -----------------------------------
# REGEX PATTERN
# -----------------------------------
log_pattern = re.compile(
    r'(\S+) (\S+) (\S+) \[(.*?)\] "(.*?)" (\d{3}) (\S+|-)'
)

def stable_hash(value: str) -> int:
    return int(hashlib.md5(value.encode()).hexdigest(), 16) % 10000

# -----------------------------------
# PARSE + PROCESS
# -----------------------------------
def process_logs(content: str) -> pd.DataFrame:
    rows = []

    for line in content.splitlines():
        m = log_pattern.match(line.strip())
        if m:
            rows.append(m.groups())

    if len(rows) < 5:
        raise ValueError("Invalid or unsupported log format")

    df = pd.DataFrame(rows, columns=[
        "ip", "ident", "authuser", "timestamp",
        "request", "status", "bytes"
    ])

    # ---- Split request ----
    req = df['request'].str.split(' ', n=2, expand=True)
    df['method'] = req[0]
    df['url'] = req[1]
    df['protocol'] = req[2]

    df = df.dropna(subset=['method', 'url', 'protocol'])

    df['protocol'] = df['protocol'].str.extract(r'(HTTP/\d\.\d)', expand=False)

    # ---- Types ----
    df['bytes'] = pd.to_numeric(df['bytes'].replace('-', '0'), errors='coerce').fillna(0)
    df['status'] = pd.to_numeric(df['status'], errors='coerce').fillna(0)

    df['timestamp'] = pd.to_datetime(
        df['timestamp'],
        format="%d/%b/%Y:%H:%M:%S %z",
        errors='coerce'
    )

    df = df.dropna(subset=['timestamp'])

    df['hour'] = df['timestamp'].dt.hour

    # ---- Features ----
    df['url_len'] = df['url'].str.len()
    df['url_depth'] = df['url'].str.count('/')

    df['is_image'] = df['url'].str.contains(
        r'\.(gif|jpg|png)', case=False, regex=True
    ).astype(int)

    df['is_html'] = df['url'].str.contains(
        r'\.html', case=False, regex=True
    ).astype(int)

    # ---- Encoding ----
    df = pd.get_dummies(df, columns=['method', 'protocol'])

    # Add missing expected columns
    for col in features:
        if col not in df.columns:
            df[col] = 0

    # IP encoding
    df['ip_enc'] = df['ip'].apply(stable_hash)

    X = df[features]

    # ---- Prediction ----
    df['prediction'] = model.predict(X)
    df['score'] = model.predict_proba(X)[:, 1]

    return df

# -----------------------------------
# ROUTES
# -----------------------------------

@app.get("/")
def root():
    return {"message": "Web Log Analyzer API Running 🚀"}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_loaded": True,
        "features": len(features)
    }


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        start = time.time()

        content = (await file.read()).decode("utf-8")

        if len(content.strip()) == 0:
            raise HTTPException(400, "Empty file")

        if len(content) > 5_000_000:
            raise HTTPException(400, "File too large")

        df = process_logs(content)

        anomalies = df[df['prediction'] == 1]

        result = {
            "total_requests": len(df),
            "error_rate": float((df['status'] >= 400).mean()),
            "top_urls": df['url'].value_counts().head(10).to_dict(),
            "status_distribution": df['status'].value_counts().to_dict(),
            "hour_distribution": df['hour'].value_counts().sort_index().to_dict(),
            "anomalies": {
                "count": int(len(anomalies)),
                "percentage": float(len(anomalies) / len(df) * 100)
            },
            "processing_time_sec": round(time.time() - start, 3)
        }

        return result

    except ValueError as e:
        raise HTTPException(400, str(e))

    except Exception as e:
        raise HTTPException(500, f"Processing failed: {str(e)}")