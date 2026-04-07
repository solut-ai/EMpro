# SCBMS‑PROD Cutover Runbook (v1) — 1 page

**Objective:** Cut over SCBMS production traffic to **LuxeVault final enforcement** using **PoM Oracle canonical verification + LuxeVault local fallback**, under the locked hard gates + 30‑rule matrix. [Source](https://www.genspark.ai/api/files/s/FHuOM92F?cache_control=3600) [Source](https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600)

**Pinned visuals (expected system behavior):**
- Swimlane enforcement wiring: https://www.genspark.ai/api/files/s/FHuOM92F?cache_control=3600 [Source](https://www.genspark.ai/api/files/s/FHuOM92F?cache_control=3600)
- 30‑rule decision flowchart: https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600 [Source](https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600)

---

## 0) Cutover inputs (must be confirmed before start)
- **Policy config (patched verify modes):**
  - `NOTE-LuxeVault-PolicyEngine-v1_FullMerged_Patched-VerifyModes_2026-02-22.min.json` (deploy)
- **Locked verification behavior (SCBMS‑PROD):**
  - Canonical verify timeout = **1000ms**
  - Canonical unreachable policy: **A0–A2 ALLOW local-only; A3–A5 DENY**
  - TTL hard gate: **≤120s**
  - Scope hard gate: **domain_scope.functions == [intent_type]** (exact match) [Source](https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600)

---

## 1) Roles & comms
- **Release Commander (RC):** owns timeline, GO/NO‑GO, rollback calls.
- **LuxeVault On‑Call:** config deploy, enforcement flags, decision metrics.
- **PoM Oracle On‑Call:** issue + canonical verify health/latency.
- **Crimson/Attestation On‑Call:** liveness/attestation pass rate; spoof anomalies.
- **DCIA/SecOps:** reviews STEP‑UP/TIMELOCK/DENY queue; investigates anomalies (“Log → DCIA” cells). [Source](https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600)

Create a shared incident channel and pin:
- Current config version / checksum
- Key registry status dashboard
- Canonical verify p95 latency chart

---

## 2) Go / No‑Go gates (must all be GREEN)
**PoM Oracle (canonical verify):**
- p95 < **1000ms**, error rate stable

**Key registry:**
- Active SCBMS‑PROD subkey present
- Revocations propagate to LuxeVault within expected cache TTL

**Crimson:**
- Liveness pass rate within baseline; no systemic device attestation failures

**LuxeVault:**
- Hard gates functioning; sample packets validate; STEP‑UP requires **2nd PoM + PIN** [Source](https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600)

---

## 3) Cutover timeline (recommended)
### T‑24h (Readiness)
- Confirm SCBMS‑PROD key active + registry reachable
- Dry‑run canonical verify from LuxeVault (service‑to‑service)
- Confirm DCIA pipeline receiving events

### T‑60m (Shadow mode)
- Enable **shadow evaluation**: evaluate rules but do not block production actions
- Validate:
  - gate failures map to expected failure codes
  - action‑class mapping is correct for SCBMS intents

### T‑15m (GO/NO‑GO)
- RC checks p95 latency, timeout rate, and deny spikes on canary users

---

## 4) Canary ramp (traffic share enforced by LuxeVault)
Ramp only if metrics are stable for the full hold period.

1) **0% → 1% (hold 10 min)**
2) **1% → 5% (hold 15 min)**
3) **5% → 25% (hold 20 min)**
4) **25% → 50% (hold 20 min)**
5) **50% → 100% (hold 30 min)**

**Watch at every step:**
- Canonical verify timeout rate (if rising, A3–A5 will DENY)
- A3–A5 DENY rate (must not surge unexpectedly)
- Key registry mismatch/unknown kid events
- Crimson liveness failures
- DCIA queue depth + processing latency

**Reminder:** Canonical unreachable ⇒ **A3–A5 DENY**, even if local verify passes; A0–A2 may proceed local-only. [Source](https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600)

---

## 5) Rollback (immediate triggers + actions)
### Trigger if any occurs (sustained > 5 minutes)
- Canonical verify timeout spike
- Key registry outage or mass unknown-kid events
- Crimson liveness pass collapses
- A3–A5 DENY spikes without a known cause

### Rollback actions
- Drop enforced traffic share back to **0%** (shadow-only)
- Keep logging on for diagnosis
- If suspected compromise: revoke SCBMS‑PROD subkey (registry → hard gate fails) [Source](https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600)

---

## 6) Post‑cutover validation (T+2h)
- Confirm steady-state: timeouts, denies, step-ups, timelocks match baseline
- Confirm canonical/local discrepancy count near zero (canonical wins)
- Write cutover note: ramp times, incidents, final status

---

## Appendix — “Correct behavior” references
- Swimlane: https://www.genspark.ai/api/files/s/FHuOM92F?cache_control=3600 [Source](https://www.genspark.ai/api/files/s/FHuOM92F?cache_control=3600)
- 30‑rule flow: https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600 [Source](https://www.genspark.ai/api/files/s/qnZbCCAo?cache_control=3600)
