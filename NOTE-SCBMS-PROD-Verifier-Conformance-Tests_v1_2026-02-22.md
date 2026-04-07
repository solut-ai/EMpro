# SCBMS‑PROD Verifier Conformance Tests (v1)

**Goal:** Prove LuxeVault **Local Verification** matches PoM Oracle **Canonical Verification** for all hard gates and policy‑critical behaviors, and that SCBMS‑PROD uses the locked dual‑verification ladder:
- Canonical verify timeout (PROD) = **1000ms**
- Canonical unreachable policy: **A0–A2 allow local‑only; A3–A5 deny**

**Visual anchors (expected behavior):**
- Swimlane flow: https://www.genspark.ai/api/files/s/FHuOM92F?cache_control=3600
- 30‑rule matrix flowchart: https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600

---

## A) Test prerequisites (setup)
1) SCBMS‑PROD key registry has at least:
   - One active SCBMS‑PROD signing key (`POK‑SCBMS‑SIGN‑PROD‑...`)
   - One revoked SCBMS‑PROD signing key
2) A working PoM Oracle Issue endpoint to mint valid packets.
3) Ability to simulate canonical verify behaviors:
   - Return PASS
   - Return FAIL (with a chosen gate)
   - Become UNREACHABLE (timeout > 1000ms)

---

## B) Conformance success criteria
A test **passes** when:
- Local verifier and canonical verifier produce the same `hard_gates` truth map and overall verdict, **or**
- In discrepancy cases, LuxeVault applies the locked ladder (**canonical wins / fail closed**) and produces the correct final enforcement outcome.

---

## C) Hard‑gate equivalence tests (G0–G5)
For each gate below, run:
- **Control**: valid packet ⇒ Local PASS, Canonical PASS
- **Fault injection**: gate fails ⇒ Local FAIL, Canonical FAIL, final result DENY

### G0 Signature validity
- C‑G0‑01: Valid signature (control)
- F‑G0‑02: Tamper payload or signature ⇒ signature_invalid

### G1 TTL ≤ 120s
- C‑G1‑01: Packet age 0–30s ⇒ ttl_valid
- F‑G1‑02: Packet expired ⇒ ttl_invalid
- F‑G1‑03: Packet claims TTL > 120s (if possible) ⇒ ttl_invalid

### G2 Environment key match (SCBMS‑PROD)
- C‑G2‑01: env=PROD, kid=SCBMS‑PROD
- F‑G2‑02: env=PROD, kid=SCBMS‑SANDBOX or wrong env ⇒ env_mismatch

### G3 Key registry active / not revoked
- C‑G3‑01: Active key
- F‑G3‑02: Revoked key
- F‑G3‑03: Unknown key id

### G4 Crimson liveness/attestation pass
- C‑G4‑01: liveness.pass=true + attestation present
- F‑G4‑02: liveness.pass=false
- F‑G4‑03: attestation missing/invalid hash ⇒ attestation_fail

### G5 Exact scope match (LOCKED)
- C‑G5‑01: intent_type=TRANSFER, functions=["TRANSFER"]
- F‑G5‑02: functions has 2 entries ⇒ scope_exact_match=false
- F‑G5‑03: functions=["WALLET_VIEW"] intent_type=TRANSFER ⇒ scope_exact_match=false

---

## D) Dual‑verification ladder tests (canonical + local fallback)

### D1 Canonical unreachable policy (LOCKED)
Simulate canonical verify timeout (>1000ms).
- D1‑A0: A0 request + local PASS + canonical UNREACHABLE ⇒ proceed local-only decision
- D1‑A1: A1 request + local PASS + canonical UNREACHABLE ⇒ proceed local-only decision
- D1‑A2: A2 request + local PASS + canonical UNREACHABLE ⇒ proceed local-only decision
- D1‑A3: A3 request + local PASS + canonical UNREACHABLE ⇒ **DENY**
- D1‑A4: A4 request + local PASS + canonical UNREACHABLE ⇒ **DENY**
- D1‑A5: A5 request + local PASS + canonical UNREACHABLE ⇒ **DENY**

### D2 Canonical FAIL overrides local PASS (canonical wins)
- D2‑01: Local PASS but canonical FAIL (any gate) ⇒ final DENY

### D3 Local FAIL short‑circuits
- D3‑01: Local FAIL (any gate) ⇒ final DENY, canonical not required

---

## E) STEP‑UP conformance tests
- E‑01: STEP‑UP decision requires **second fresh PoM packet (≤120s) + PIN**
- E‑02: second packet missing ⇒ action not released
- E‑03: PIN invalid 3 times ⇒ lockout triggers per action class policy

---

## F) Audit / DCIA logging tests
For any STEP‑UP/TIMELOCK/DENY or any A3–A5:
- F‑01: ensure log includes decision_id, kid, hard_gates map, canonical latency/outcome, reason codes
- F‑02: ensure canonical unreachable logs the timeout and class policy applied

---

## G) Minimal test matrix (recommended execution order)
1) C‑G0‑01 (control) to confirm baseline
2) Fault injections G0→G5
3) Canonical unreachable ladder (D1)
4) Canonical fail overrides (D2)
5) STEP‑UP release path tests (E)
6) Logging tests (F)

---

## H) Deliverables
- Test run report (pass/fail + notes)
- Captured example packets (redacted)
- Log extracts proving enforcement outcomes
