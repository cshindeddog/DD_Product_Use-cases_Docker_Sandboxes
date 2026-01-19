import os
import json
import base64
import gzip
from io import BytesIO

SECRET_HEADER = os.getenv("DD_SHARED_SECRET_HEADER", "x-dd-secret")
SECRET_VALUE  = os.getenv("DD_SHARED_SECRET_VALUE", "abc123abc")

def _maybe_b64decode(body: str) -> bytes:
    # Lambda Function URL often passes body as a string; it can be raw text or base64
    # We'll try base64 decode first; if it fails, treat it as raw bytes.
    try:
        return base64.b64decode(body, validate=True)
    except Exception:
        return body.encode("utf-8")

def _gunzip(data: bytes) -> bytes:
    return gzip.decompress(data)

def lambda_handler(event, context):
    headers = { (k.lower()): v for k, v in (event.get("headers") or {}).items() }

    # 1) Auth check (simple shared secret header)
    if SECRET_VALUE:
        got = headers.get(SECRET_HEADER.lower())
        if got != SECRET_VALUE:
            return {"statusCode": 401, "body": "unauthorized"}

    # 2) Get body
    body = event.get("body", "")
    if body is None:
        body = ""

    # 3) Lambda sometimes tells you whether body is base64 encoded
    is_b64 = bool(event.get("isBase64Encoded"))
    raw = base64.b64decode(body) if is_b64 else _maybe_b64decode(body)

    # 4) GZIP decode if needed
    content_encoding = headers.get("content-encoding", "").lower()
    if "gzip" in content_encoding:
        raw = _gunzip(raw)
    else:
        # Datadog forwarding usually gzips; if not, this still works
        pass

    # 5) Parse JSON payload
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as e:
        # Helpful for debugging: log first bytes
        print("Failed to parse JSON:", str(e))
        print("First 200 bytes:", raw[:200])
        return {"statusCode": 400, "body": "bad request"}

    # 6) Inspect structure (often list/batch)
    if isinstance(payload, list):
        print(f"Received batch: {len(payload)} logs")
        for i, item in enumerate(payload[:3]):
            print(f"Sample[{i}]: {json.dumps(item)[:1000]}")
    else:
        print("Received payload object")
        print(json.dumps(payload)[:2000])

    return {"statusCode": 200, "body": "ok"}

