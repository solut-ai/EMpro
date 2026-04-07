# SCBMS‑PROD Rollout Deployment Checklist (v1)

**Scope:** SCBMS (Production) with LuxeVault as Final Enforcement; PoM Oracle canonical verification + LuxeVault local fallback; PoM TTL ≤ 120s; 30‑rule decision matrix A0–A5 × R0–R4.

**Visual anchors (implementation references):**
- LuxeVault Trigger System — Swimlane Flow: https://www.genspark.ai/api/files/s/FHuOM92F?cache_control=3600
- LuxeVault PoM Rules (30 rules): https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600

---

## 0) Release artifacts (confirm correct build)
- [ ] Deploy the **patched** policy config (minified preferred):
  - `NOTE-LuxeVault-PolicyEngine-v1_FullMerged_Patched-VerifyModes_2026-02-22.min.json`
  - (Pretty/reference) `NOTE-LuxeVault-PolicyEngine-v1_FullMerged_Patched-VerifyModes_2026-02-22.json`
- [ ] Confirm the 30‑rule flowchart is present for review:
  - `NOTE-Infographic-LuxeVault-PoM-Rules_30Rules_Flowchart_16x9_2026-02-22.png`

---

## 1) Key governance + SCBMS‑PROD subkey readiness
- [ ] Root governance available (3‑of‑5) for emergency actions and key lifecycle.
- [ ] Create/activate SCBMS‑PROD signing subkey: `POK‑SCBMS‑SIGN‑PROD‑{YYYYMMDD}`.
- [ ] Key Registry reachable by LuxeVault (active vs revoked) and includes SCBMS/PROD scope.
- [ ] Rotation cadence locked: **SCBMS‑PROD rotates every 30 days**.

---

## 2) Project Crimson (attestation boundary) readiness
- [ ] Client apps integrated with Crimson sensing + attestation.
- [ ] Liveness is produced consistently (`liveness.pass=true` when valid) and stable confidence reporting.
- [ ] Crimson failure path validated: hard‑gate fail ⇒ DENY.

---

## 3) PoM Oracle service readiness (Issue + Canonical Verify)
- [ ] Issue endpoint produces PoM Intent Packet with **server‑computed** `expires_utc` and TTL ≤ 120s.
- [ ] Exact match lock enforced: `domain_scope.functions == [intent_type]` (single item).
- [ ] Canonical verify endpoint reachable from LuxeVault (service‑to‑service only).
- [ ] Canonical verify client timeout locked: **1000ms**.

---

## 4) LuxeVault enforcement readiness (SCBMS‑PROD)
- [ ] Patched config deployed into SCBMS‑PROD runtime.
- [ ] Hard gates enabled:
  - Signature valid
  - TTL ≤ 120s
  - Env key match
  - Key registry active
  - Crimson liveness/attestation pass
  - Scope exact match
- [ ] Dual verification (locked) implemented:
  - Local verify first
  - Canonical verify required for A3–A5; optional for A0–A2
  - Canonical unreachable policy (locked):
    - A0–A2: ALLOW local-only
    - A3–A5: DENY
- [ ] STEP‑UP enforcement matches rules: **second fresh PoM packet + PIN**.

---

## 5) End‑to‑end conformance (must pass before go‑live)
- [ ] Hard‑gate failure tests: each gate failure ⇒ DENY.
- [ ] Canonical unreachable tests:
  - A0–A2 canonical timeout ⇒ local-only proceeds
  - A3–A5 canonical timeout ⇒ DENY
- [ ] Rule matrix spot checks (representative):
  - A1 + R3 ⇒ TIMELOCK 1h
  - A4 + R2 ⇒ TIMELOCK 24h
  - A5 + R2 ⇒ TIMELOCK 24h

---

## 6) Monitoring + DCIA logging readiness
- [ ] Log decision_id, action_class, risk_score, reason_codes, kid, TTL outcome, canonical latency/outcome.
- [ ] Alerts configured:
  - Canonical verify timeout rate
  - DENY spikes (A3–A5)
  - Key registry mismatch errors
  - Crimson liveness failure spikes

---

## 7) Key rotation dry run (SCBMS‑PROD)
- [ ] Rotate SCBMS‑PROD subkey with overlap (new active before old revoked).
- [ ] Confirm revoked key instantly fails verification.

---

## 8) Go‑live sequence
- [ ] Canary: internal accounts only
- [ ] Limited cohort rollout
- [ ] Full rollout

---

## 9) Rollback + emergency controls
- [ ] Root governance emergency revoke tested.
- [ ] Freeze Mode runbook validated.
