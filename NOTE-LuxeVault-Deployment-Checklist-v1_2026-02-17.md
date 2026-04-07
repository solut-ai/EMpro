# LuxeVault Policy Engine v1.0 — Deployment Checklist

**Generated**: 2026-02-17  
**Issuer**: Middleton Solutions Incorporated (MSI-001, EIN 47-3650823)  
**Config File**: `NOTE-LuxeVault-PolicyEngine-v1_FullMerged_2026-02-17.json`

---

## Pre-Deployment Verification

### 1. Key Governance Setup
- [ ] **Root Authority**: Confirm 3-of-5 multi-sig wallet is deployed
- [ ] **Keyholder Distribution**: Verify all 5 keyholders have secure custody
  - Security Lead
  - Exchange Ops Lead
  - Monitoring/Compliance Lead
  - Corporate Governance Rep
  - Independent Backup Holder
- [ ] **Subkey Generation**: Create initial subkeys for PROD environment
  - `POK-SCBMS-SIGN-PROD-{YYYYMMDD}`
  - `POK-DCIA-SIGN-PROD-{YYYYMMDD}`
  - `POK-MC-SIGN-PROD-{YYYYMMDD}`
- [ ] **HSM/Key Vault**: Deploy hardware security module or equivalent for Root keys
- [ ] **Key Registry**: Deploy active/revoked key registry accessible by all consumers

### 2. Project Crimson Integration
- [ ] **Device Attestation**: Confirm Crimson SDK deployed to client devices
- [ ] **Liveness Check**: Verify anti-spoof liveness detection active
- [ ] **Secure Enclave**: Confirm local signing in TPM/secure enclave
- [ ] **Privacy Model**: Validate raw biometrics stay on-device
- [ ] **Multi-Modal Fusion**: Test facial expression + additional sensor inputs

### 3. PoM Oracle Deployment
- [ ] **Intent Packet Signing**: Deploy PoM Oracle service with subkey access
- [ ] **TTL Enforcement**: Confirm 120-second expiry enforcement
- [ ] **Risk Score Engine**: Deploy 0-100 scoring with reason codes
- [ ] **Policy Engine Integration**: Wire PoM outputs to LuxeVault decision logic
- [ ] **DCIA Feed**: Confirm event stream to DCIA monitoring layer

### 4. LuxeVault Policy Engine
- [ ] **Config Upload**: Deploy `NOTE-LuxeVault-PolicyEngine-v1_FullMerged_2026-02-17.json`
- [ ] **Hard Gates**: Test all 5 hard gates (signature, TTL, key match, registry, liveness)
- [ ] **Risk Band Mapping**: Verify R0-R4 score ranges (0-100)
- [ ] **Action Class Registry**: Confirm A0-A5 intent type mappings
- [ ] **Rule Execution**: Test ALLOW/STEP_UP/TIMELOCK/DENY decisions
- [ ] **Freeze Mode**: Test emergency freeze activation (3-of-5 approval)

### 5. PIN & Step-Up System
- [ ] **PIN Storage**: Deploy hashed PIN storage (bcrypt/Argon2)
- [ ] **Class-Specific Lockout**: Verify lockout times by action class
  - A0: 1 hour (3600s)
  - A1: 4 hours (14400s)
  - A2-A5: 24 hours (86400s)
- [ ] **Second Packet Requirement**: Test fresh PoM packet within 120s
- [ ] **PIN Validation**: Confirm out-of-band PIN check before release
- [ ] **Support Override**: Deploy support ticket + verification workflow
- [ ] **Post-Override PIN Reset**: Enforce 15-min window + high-risk block

### 6. CBB3 Program Integration
- [ ] **Issuance Trigger**: Test `BOND_ISSUANCE` intent → vault record creation
- [ ] **Cash-In Validation**: Confirm $11,000 payment capture
- [ ] **Token Delivery**: Verify 10,000 CBB3 tokens @ $1.00 each issued immediately
- [ ] **Premium Accounting**: Book $1,000 as non-refundable fee at Day 0
- [ ] **Maturity Calculator**: Deploy 90-day + 10% APR simple interest (30/360) engine
- [ ] **Redemption Trigger**: Test `BOND_REDEMPTION` → $10,250 payout enforcement
- [ ] **DCIA Audit Log**: Confirm all issuance/redemption events logged

---

## Integration Testing

### Phase 1: Unit Tests (Sandbox Environment)
- [ ] Test each hard gate individually (force failures)
- [ ] Test risk band boundaries (scores 19, 20, 39, 40, etc.)
- [ ] Test each action class + risk band combination (30 rules)
- [ ] Test PIN lockout at 3 attempts
- [ ] Test TTL expiry (119s pass, 121s fail)
- [ ] Test revoked subkey rejection
- [ ] Test support override flow (ticket + verification)
- [ ] Test PIN reset enforcement post-override

### Phase 2: Integration Tests (Sandbox → Test)
- [ ] End-to-end: Device → Crimson → PoM Oracle → LuxeVault → SCBMS
- [ ] CBB3 full cycle: issuance → hold → redemption
- [ ] Freeze mode activation: 3-of-5 approval → policy override
- [ ] Key rotation: generate new subkey → activate → revoke old
- [ ] Cross-system: SCBMS + DCIA + MiddletonChain subkey isolation

### Phase 3: Load Testing (Test Environment)
- [ ] 1,000 concurrent PoM Intent Packets
- [ ] Burst traffic: 10,000 requests in 60 seconds
- [ ] Subkey signing latency < 200ms p95
- [ ] DCIA event ingestion lag < 5 seconds

---

## Security Audit

### External Review
- [ ] **Smart Contract Audit**: If on-chain components deployed
- [ ] **Penetration Test**: Third-party security firm assessment
- [ ] **Cryptographic Review**: Validate signature schemes, key derivation
- [ ] **Privacy Audit**: Confirm no PII/biometric leakage on-chain

### Internal Review
- [ ] **Access Control Matrix**: Document who can trigger Freeze Mode, revoke keys, override PIN
- [ ] **Incident Response Plan**: Define procedures for key compromise, oracle outage, DCIA failure
- [ ] **Compliance Check**: Confirm alignment with securities law (Reg D, accredited investor rules)
- [ ] **Data Retention Policy**: Define log retention periods, GDPR/CCPA compliance

---

## Production Deployment

### Go-Live Sequence
1. [ ] **T-7 days**: Deploy config to PROD (freeze_mode: enabled initially)
2. [ ] **T-3 days**: Onboard first pilot users (internal staff only)
3. [ ] **T-1 day**: Deploy Root multi-sig + initial PROD subkeys
4. [ ] **T-0 (Go-Live)**: Disable freeze mode via 3-of-5 approval
5. [ ] **T+1 day**: Monitor first 24h, review DCIA alerts
6. [ ] **T+7 days**: First PROD subkey rotation (30-day clock starts)

### Monitoring & Alerts
- [ ] **DCIA Dashboard**: Real-time risk score distribution, DENY rate, TIMELOCK queue depth
- [ ] **PoM Oracle Health**: Intent packet signing latency, TTL violation rate
- [ ] **Crimson Attestation**: Liveness failure rate, device spoof detection count
- [ ] **Subkey Status**: Active/revoked key registry, rotation schedule tracker
- [ ] **CBB3 Program**: Issuance volume, redemption queue, premium revenue tracking

### Escalation Contacts
- **Root Authority Emergency**: [3-of-5 keyholder contact list]
- **PoM Oracle Ops**: [Oracle service team]
- **DCIA Monitoring**: [Security ops team]
- **Support Override Team**: [Ticket system + approval chain]

---

## Post-Deployment

### Week 1
- [ ] Daily review of DCIA alert feed
- [ ] Manual spot-check of STEP_UP/TIMELOCK decisions
- [ ] Validate first CBB3 issuance (if applicable)
- [ ] Confirm no unauthorized subkey signing

### Week 2-4
- [ ] Weekly review of policy effectiveness (false positive/negative rates)
- [ ] Adjust risk band thresholds if needed (requires config update)
- [ ] First scheduled PROD subkey rotation (Day 30)

### Month 2-3
- [ ] Quarterly security audit
- [ ] Review PIN lockout patterns (legitimate vs. attack)
- [ ] Evaluate support override usage (abuse detection)
- [ ] Plan SANDBOX/TEST subkey rotations (Day 90/180)

---

## Rollback Plan

### Emergency Scenarios
- **Freeze Mode Activation**: 3-of-5 approval → all A3/A4/A5 → TIMELOCK
- **Oracle Outage**: Fallback to static risk score = 50 (STEP_UP for A3+)
- **Crimson Failure**: Block mint/redeem/large transfers, manual review only
- **Key Compromise**: Immediate revocation via Root Authority → deploy new subkey within 1 hour

### Config Rollback
- [ ] Maintain previous 3 config versions in git/vault
- [ ] Test rollback procedure in SANDBOX monthly
- [ ] Document rollback approval chain (Root Authority or designated ops lead)

---

## Evidence & Documentation

### Live Deployment URLs
- **LuxeVault Site**: https://luxevault.otfz.cloud (503 as of 2026-02-17, pending deployment)
- **OTFZ Main**: https://otfz.cloud (200 OK, homepage active)
- **Square CBB3 Listing**: https://middletonsolutions.square.site/product/cbb3/VE6OZJW6RY23AYRZ7XAVQ4L6
- **OpenSea Collection**: https://opensea.io/collection/scbmscbb3

### Visual Assets
- **Swimlane Flow Diagram**: https://www.genspark.ai/api/files/s/FHuOM92F?cache_control=3600
- **CBB3 Term Sheet + Cashflow**: https://www.genspark.ai/api/files/s/iCi8uIwK?cache_control=3600
- **MSI Org Chart + ORCA/OTFZ**: https://www.genspark.ai/api/files/s/96YpxggV?cache_control=3600

### Private Drive Archive
- **Config JSON**: `/MKMANAGEMENT/NOTE-LuxeVault-PolicyEngine-v1_FullMerged_2026-02-17.json`
- **Drive URL**: https://www.genspark.ai/aidrive/files/MKMANAGEMENT

---

## Sign-Off

- [ ] **Technical Lead**: _________________________ Date: _______
- [ ] **Security Lead**: _________________________ Date: _______
- [ ] **Compliance Officer**: _________________________ Date: _______
- [ ] **Root Authority (3-of-5)**: 
  - [ ] Keyholder 1: _________________________ Date: _______
  - [ ] Keyholder 2: _________________________ Date: _______
  - [ ] Keyholder 3: _________________________ Date: _______

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-17  
**Next Review**: 2026-03-17 (30 days)
