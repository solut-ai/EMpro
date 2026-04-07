"""LuxeVault PoM Oracle Mock Generator (v1)

Purpose
- Generate mock PoM Intent Packets + Risk Scores for integration testing.
- Enforces TTL <= 120 seconds (locked).
- Uses a simple HMAC signature for demo ONLY (replace with your real signing).

Outputs
- intent_packet: JWT-style (header.payload.signature) where payload is JSON
- risk_score: JSON object + signature

NOTE
- This is a test harness; do NOT use this signing in production.
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime, timezone

DEFAULT_TTL_SECONDS = 120


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso_from_epoch(epoch: int) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hmac_sign(secret: bytes, msg: bytes) -> str:
    sig = hmac.new(secret, msg, hashlib.sha256).digest()
    return b64url(sig)


def make_intent_packet(
    issuer: str,
    signing_key_id: str,
    domain_scope: dict,
    intent_type: str,
    user_scope: str,
    liveness_pass: bool,
    liveness_confidence: float,
    intent_confidence: float,
    ttl_seconds: int,
    device_attestation_hash: str,
    secret: bytes,
):
    now = int(time.time())
    exp = now + min(ttl_seconds, DEFAULT_TTL_SECONDS)

    header = {
        "typ": "POM-JWT",
        "alg": "HS256-DEMO",
        "kid": signing_key_id,
    }

    payload = {
        "pomid": f"POM-{uuid.uuid4().hex}",
        "timestamp_utc": iso_from_epoch(now),
        "expires_utc": iso_from_epoch(exp),
        "issuer": issuer,
        "signing_key_id": signing_key_id,
        "domain_scope": domain_scope,
        "device_attestation_hash": device_attestation_hash,
        "liveness": {
            "pass": bool(liveness_pass),
            "confidence": float(liveness_confidence),
        },
        "intent_type": intent_type,
        "intent_confidence": float(intent_confidence),
        "user_scope": user_scope,
        "nonce": uuid.uuid4().hex,
    }

    header_b64 = b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = b64url(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature_b64 = hmac_sign(secret, signing_input)

    token = f"{header_b64}.{payload_b64}.{signature_b64}"
    return token, payload


def make_risk_score(
    issuer: str,
    signing_key_id: str,
    domain_scope: dict,
    intent_type: str,
    risk_score: int,
    reason_codes: list,
    recommended_action: str,
    secret: bytes,
):
    obj = {
        "riskid": f"RSK-{uuid.uuid4().hex}",
        "timestamp_utc": utc_now_iso(),
        "issuer": issuer,
        "signing_key_id": signing_key_id,
        "domain_scope": domain_scope,
        "intent_type": intent_type,
        "risk_score": int(risk_score),
        "reason_codes": list(reason_codes),
        "recommended_action": recommended_action,
    }

    msg = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    obj["signature"] = hmac_sign(secret, msg)
    obj["signature_alg"] = "HS256-DEMO"
    return obj


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--issuer", default="PoM-Oracle")
    p.add_argument("--signing_key_id", default="POK-SCBMS-SIGN-PROD-YYYYMMDD")
    p.add_argument("--system", choices=["SCBMS", "DCIA", "MC"], default="SCBMS")
    p.add_argument("--env", choices=["PROD", "SANDBOX", "TEST"], default="PROD")
    p.add_argument("--intent_type", default="TRANSFER")
    p.add_argument("--user_scope", default="user:demo")
    p.add_argument("--ttl", type=int, default=120)
    p.add_argument("--risk_score", type=int, default=42)
    p.add_argument("--reason_codes", default="VELOCITY_SPIKE,ANOMALOUS_LOCATION")
    p.add_argument("--recommended_action", default="STEP_UP", choices=["ALLOW", "STEP_UP", "TIMELOCK", "DENY"])
    p.add_argument("--liveness_pass", action="store_true")
    p.add_argument("--liveness_confidence", type=float, default=0.92)
    p.add_argument("--intent_confidence", type=float, default=0.88)
    p.add_argument("--device_attestation_hash", default="sha256:demo_attestation")
    p.add_argument("--secret", default=os.getenv("POM_MOCK_SECRET", "change-me"))

    args = p.parse_args()

    domain_scope = {
        "system": args.system,
        "environment": args.env,
        "functions": [args.intent_type],
    }

    secret = args.secret.encode("utf-8")

    token, payload = make_intent_packet(
        issuer=args.issuer,
        signing_key_id=args.signing_key_id,
        domain_scope=domain_scope,
        intent_type=args.intent_type,
        user_scope=args.user_scope,
        liveness_pass=args.liveness_pass,
        liveness_confidence=args.liveness_confidence,
        intent_confidence=args.intent_confidence,
        ttl_seconds=args.ttl,
        device_attestation_hash=args.device_attestation_hash,
        secret=secret,
    )

    risk = make_risk_score(
        issuer=args.issuer,
        signing_key_id=args.signing_key_id,
        domain_scope=domain_scope,
        intent_type=args.intent_type,
        risk_score=args.risk_score,
        reason_codes=[c.strip() for c in args.reason_codes.split(",") if c.strip()],
        recommended_action=args.recommended_action,
        secret=secret,
    )

    out = {
        "intent_packet_jwt": token,
        "intent_packet_payload": payload,
        "risk_score": risk,
    }

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
