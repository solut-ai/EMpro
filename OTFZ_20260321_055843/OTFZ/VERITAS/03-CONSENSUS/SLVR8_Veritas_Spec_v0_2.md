# SLVR8 / Veritas Specification
## v0.2-draft for MiddletonChain-aligned implementation planning

Status: Draft  
Date: 2026-03-21  
Launch date: 2026-03-21  
Target run date: 2026-06-21

---

## 1. Scope

This document defines the current working specification for **Veritas** consensus and the **SLVR8** hashing / identity suite as used in the OTFZ technical narrative. It consolidates prior draft notes on AIR, wire format, pseudocode, slashing, epoch transitions, and PoM boundary logic into one file for future build and ingest use.

The public whitepaper positions Veritas and SLVR8 as core infrastructure for transactions, scale, and digital-financial logic, while CometBFT provides a practical BFT reference model for round-based consensus phases and >2/3 quorum behavior [Source](https://outthefreezer.square.site/whitepaper) [Source](https://docs.cometbft.com/main/spec/consensus/consensus)

---

## 2. Design goals

The design goals of this draft are:
- deterministic transaction ordering
- rapid finality in a permissioned validator environment
- clean separation between consensus-critical logic and advisory AI logic
- canonical hashing of important objects
- future support for audit, bridge intent verification, and evidence handling
- compatibility with a calm, explainable operating model suitable for AIR-assisted interfaces

Bitcoin remains the foundational historical example of solving digital double-spending through network consensus, while Veritas is framed here as a validator-governed BFT environment rather than a proof-of-work network [Source](https://bitcoin.org/bitcoin.pdf)

---

## 3. System model

### 3.1 Network type
Veritas is treated in this draft as a **permissioned or semi-permissioned stake-weighted BFT network**.

### 3.2 Fault model
The safety target assumes a validator set satisfying:
- `N >= 3f + 1`
- a safety / commit quorum of `> 2/3` voting power

This is aligned with the standard BFT model summarized in CometBFT documentation, where the network tolerates fewer than one-third Byzantine faults and advances via round-based voting [Source](https://docs.cometbft.com/main/spec/consensus/consensus)

### 3.3 Time model
The network is only partially synchronous. Liveness is expected after network conditions stabilize sufficiently for validators to exchange proposal and vote messages.

---

## 4. Roles

### 4.1 Validator
Maintains state, proposes blocks when selected, prevotes, precommits, signs commits, and processes evidence.

### 4.2 Observer
Tracks chain state and verifies outputs but does not vote.

### 4.3 Proposer
A validator selected for a round to broadcast the candidate block.

### 4.4 AIR / Spektraxa interface
Provides guidance, payload preparation, operator summaries, and optional attestation attachments. AIR does not finalize blocks and does not replace quorum.

### 4.5 PoM attestor
Optional auxiliary component that may attach intent or device-linked metadata for workflow enrichment. PoM does not independently determine consensus finality in this draft.

---

## 5. Consensus overview

At each height, validators run a round-based protocol. The practical reference sequence is:

`NewHeight -> Propose -> Prevote -> Precommit -> Commit -> NewHeight`

The CometBFT specification explicitly describes rounds as composed of **Propose, Prevote, and Precommit**, plus **Commit** and **NewHeight**, and uses a `+2/3` threshold meaning strictly more than two-thirds of voting power [Source](https://docs.cometbft.com/main/spec/consensus/consensus)

### 5.1 Proposal rule
The proposer broadcasts a block candidate for `(height, round)`.

### 5.2 Prevote rule
Each validator checks structural validity, proposer eligibility, and local safety constraints, then prevotes for the candidate block or `<nil>`.

### 5.3 Precommit rule
After observing a valid lock condition or other round-valid evidence, each validator precommits the block or `<nil>`.

### 5.4 Commit rule
A block is finalized when validators observe `> 2/3` precommit voting power for the same block at the same height.

---

## 6. Launch profile and target profile

### 6.1 Conservative launch profile
- block time target: 2 seconds
- expected finality target: 2 to 4 seconds
- validator set: 4 to 20 validators
- primary aim: stability, determinism, operator visibility

### 6.2 Aspirational profile
- block time target: 1 second
- throughput target: 10,000+ TPS in public positioning
- longer-term aspiration: 50,000+ TPS
- average fee target in public materials: less than $0.01

These performance claims appear in the current whitepaper narrative and should be treated as platform goals rather than guaranteed measured production numbers until benchmarked [Source](https://outthefreezer.square.site/whitepaper)

---

## 7. SLVR8 hashing suite

### 7.1 Purpose
SLVR8 provides a domain-separated hashing scheme for canonical chain objects.

### 7.2 Base function
Current draft definition:

```text
SLVR8_HASH(domain, message) = SHA256("SLVR8/V0.2/" || domain || SHA256(message))
```

### 7.3 Domains
Recommended domain labels:
- `BLOCK_HEADER`
- `BLOCK_BODY`
- `TX`
- `RECEIPT`
- `VOTE`
- `QC`
- `VALIDATOR_SET`
- `AIR_SESSION`
- `AIR_REQUEST`
- `AIR_ATTESTATION`
- `EVIDENCE`
- `INTENT`

### 7.4 Rationale
Domain separation reduces ambiguity across serialized objects and helps ensure that a transaction hash cannot be confused with a vote hash or header hash.

---

## 8. Canonical encoding rules

All consensus-critical objects must serialize deterministically.

### 8.1 Primitive rules
- unsigned integers are encoded in big-endian form
- booleans are encoded as one byte (`0x00` or `0x01`)
- byte arrays are length-prefixed
- strings use UTF-8 with length prefix
- vectors are length-prefixed and preserve order
- absent values are encoded as explicit zero-length or presence-tagged fields

### 8.2 Canonicality rule
Two honest nodes serializing the same logical object must produce identical bytes.

### 8.3 Hashing rule
Hashes are computed over canonical bytes only.

---

## 9. Core object model

### 9.1 BlockHeader
Required fields:
- version
- chain_id
- height
- round
- epoch
- timestamp_ms
- parent_block_id
- tx_root
- receipt_root
- evidence_root
- validator_set_hash
- proposer_id
- body_hash
- header_extensions

### 9.2 BlockBody
Required fields:
- transactions
- evidence_list
- optional AIR attachments
- metadata map

### 9.3 Transaction
Required fields:
- version
- tx_type
- sender
- nonce
- fee_asset
- fee_amount
- payload
- memo
- signature_list

### 9.4 Vote
Required fields:
- version
- chain_id
- height
- round
- vote_type
- block_id_or_nil
- validator_id
- validator_power
- timestamp_ms
- signature

### 9.5 QuorumCertificate (QC)
Required fields:
- version
- chain_id
- height
- round
- vote_type
- block_id
- validator_set_hash
- bitmap
- aggregated_signature_or_signature_set

### 9.6 ValidatorSet
Required fields:
- version
- epoch
- validator_entries
- total_voting_power
- set_nonce

### 9.7 AIRSession / AIRRequest / AIRAttestation
These objects are not consensus-finalizing by themselves, but they may be recorded, referenced, or attached to transactions and audit trails.

---

## 10. Transaction classes

Recommended initial classes:
- `TRANSFER`
- `STAKE_BOND`
- `STAKE_UNBOND`
- `VALIDATOR_JOIN`
- `VALIDATOR_EXIT`
- `GOVERNANCE_PROPOSAL`
- `GOVERNANCE_VOTE`
- `EVIDENCE_SUBMIT`
- `ATTESTATION_ATTACH`
- `BRIDGE_INTENT`
- `BRIDGE_FINALIZE`
- `TREASURY_ACTION`

---

## 11. Proposer selection

### 11.1 Initial method
Use stake-weighted round-robin proposer selection with deterministic ordering.

### 11.2 Future option
A VRF-based or randomness-assisted proposer schedule may be added later.

### 11.3 Deterministic rule
All nodes must derive the same proposer from the same validator set and round.

---

## 12. Validator safety rules

A validator must not:
- sign two conflicting proposals for the same height / round if acting as proposer
- prevote two conflicting block IDs for the same height / round
- precommit two conflicting block IDs for the same height / round
- violate locking rules without valid unlock conditions

These are classical BFT safety expectations and should be slashable when provable.

---

## 13. Locking and unlock logic

### 13.1 Lock condition
A validator may lock on a block after observing the required prevote threshold.

### 13.2 Unlock condition
A validator may unlock when it sees a later valid condition meeting the protocol’s unlock rule, such as a higher-round proof-of-lock-change equivalent.

### 13.3 Nil handling
If a validator cannot safely support the proposed block, it may vote `<nil>`.

The CometBFT reference uses the notion of a PoLC generated by `+2/3` prevotes, and also describes `<nil>` prevotes and precommits as part of normal progress through unsuccessful rounds [Source](https://docs.cometbft.com/main/spec/consensus/consensus)

---

## 14. Finalization

A block becomes final when:
1. it is structurally valid,
2. it has the expected block ID,
3. validators observe `> 2/3` precommit voting power for that block at the same height and round,
4. the resulting QC verifies against the validator set.

Once final, the block is appended to canonical state and its receipts become part of verifiable history.

---

## 15. Quorum certificate verification

A QC verifier must check:
- chain ID matches local configuration
- height and round are consistent
- block ID matches the committed candidate
- validator set hash matches the active epoch set
- signer bitmap references valid validators
- signatures verify for the message digest
- cumulative voting power represented by signatures is `> 2/3`

---

## 16. AIR interface boundary

AIR is the conversational handle for the Spektraxa intelligence layer, not the finality engine.

AIR may:
- prepare summaries
- draft transaction intents
- attach non-final advisory context
- produce operator-facing explanations
- help translate technical workflows into plain language

AIR may not:
- override validator votes
- unilaterally finalize state
- bypass treasury or compliance controls
- replace QC validation

This separation preserves a calm, useful AI interface without allowing the advisory layer to silently become a consensus authority.

---

## 17. Proof-of-Mind boundary

Proof-of-Mind is treated here as an optional attestation and enrichment layer.

Potential inputs mentioned in project drafts include device-linked signals, facial expression inputs, wearable devices, and other future device surfaces. In this specification, those ideas remain outside the finality-critical path unless formal governance later moves any subset into a tightly specified and auditable role.

### 17.1 Current rule
No raw biometric or device-stream input is required for block validity.

### 17.2 Current allowed use
PoM results may be attached as advisory metadata, scoring, or operator signals.

### 17.3 Privacy rule
Keep raw biometric streams off-chain.

---

## 18. Evidence and slashing

### 18.1 Slashable events
- double proposal
- double prevote
- double precommit
- invalid signer spoofing
- downtime beyond tolerated threshold
- forged QC construction attempts
- censorship or withholding patterns when provable and policy-defined

### 18.2 Penalty classes
- **Severe:** slash + jail + removal proposal
- **Moderate:** slash + temporary suspension
- **Mild:** missed-block penalties or reward reduction

### 18.3 Evidence structure
Evidence should include:
- type
- chain_id
- height
- round
- accused_validator
- conflicting objects
- object hashes
- timestamps
- submitter
- optional AIR notes

---

## 19. Epoch transitions

### 19.1 Epoch purpose
Epochs define stable windows for validator-set membership.

### 19.2 Initial recommendation
Use fixed-length epochs and only apply validator-set changes at epoch boundaries.

### 19.3 Transition rule
The final block of an epoch contains the next validator set commitment or a pointer to it. The first block of the next epoch activates that set.

### 19.4 Safety rule
A QC for a height must always be verified against the validator set active at that height.

---

## 20. User and bridge intent model

Veritas may support bridge-related flows through explicit intent objects.

A bridge intent should minimally include:
- source_chain
- destination_chain
- asset_id
- amount_or_token_set
- sender
- recipient
- nonce
- expiry
- policy flags
- intent hash

Intent hashes should be derived through canonical encoding and the `INTENT` domain of SLVR8.

---

## 21. Wire format and pseudocode

This section defines the high-level canonical byte layout and procedural logic.

### 21.1 Canonical field encoding

```text
u8      = 1 byte unsigned integer
u16     = 2 byte unsigned integer, big-endian
u32     = 4 byte unsigned integer, big-endian
u64     = 8 byte unsigned integer, big-endian
bytes   = u32 length || raw bytes
string  = bytes(utf8)
vec<T>  = u32 item_count || item_1 || item_2 || ...
bool    = 0x00 or 0x01
```

### 21.2 BlockHeader wire layout

```text
BlockHeader :=
    u16 version
    string chain_id
    u64 height
    u32 round
    u64 epoch
    u64 timestamp_ms
    bytes parent_block_id
    bytes tx_root
    bytes receipt_root
    bytes evidence_root
    bytes validator_set_hash
    bytes proposer_id
    bytes body_hash
    bytes header_extensions
```

### 21.3 Vote wire layout

```text
Vote :=
    u16 version
    string chain_id
    u64 height
    u32 round
    u8 vote_type          // 1=prevote, 2=precommit
    bool is_nil
    bytes block_id
    bytes validator_id
    u64 validator_power
    u64 timestamp_ms
    bytes signature
```

### 21.4 QC wire layout

```text
QC :=
    u16 version
    string chain_id
    u64 height
    u32 round
    u8 vote_type
    bytes block_id
    bytes validator_set_hash
    bytes bitmap
    vec<bytes> signatures
```

### 21.5 AIR session wire layout

```text
AIRSession :=
    u16 version
    bytes session_id
    bytes actor_id
    u64 created_at_ms
    u64 expires_at_ms
    bytes nonce
    bytes permission_flags
```

### 21.6 Pseudocode: canonical hashing

```python
PREFIX = b"SLVR8/V0.2/"

def sha256(data: bytes) -> bytes:
    return SHA256(data)

def slvr8_hash(domain: bytes, message: bytes) -> bytes:
    return sha256(PREFIX + domain + sha256(message))
```

### 21.7 Pseudocode: proposer selection

```python
def select_proposer(validators, height, round_number):
    ordered = sort_by_validator_id(validators)
    total = sum(v.power for v in ordered)
    cursor = (height + round_number) % total
    running = 0
    for v in ordered:
        running += v.power
        if cursor < running:
            return v
    return ordered[-1]
```

### 21.8 Pseudocode: proposal validation

```python
def validate_proposal(block, expected_proposer, validator_set_hash):
    if block.header.proposer_id != expected_proposer.id:
        return False
    if block.header.validator_set_hash != validator_set_hash:
        return False
    if slvr8_hash(b"BLOCK_BODY", encode_block_body(block.body)) != block.header.body_hash:
        return False
    if slvr8_hash(b"BLOCK_HEADER", encode_block_header(block.header)) != block.block_id:
        return False
    return True
```

### 21.9 Pseudocode: prevote / precommit flow

```python
def on_proposal(state, block):
    proposer = select_proposer(state.validators, state.height, state.round)
    if not validate_proposal(block, proposer, state.validator_set_hash):
        return prevote_nil()
    if violates_lock_rules(state, block):
        return prevote_nil()
    return prevote_block(block.block_id)


def on_prevote_quorum(state, block_id, voting_power):
    if voting_power > state.total_power * 2 / 3 and block_id is not None:
        state.locked_block_id = block_id
        return precommit_block(block_id)
    if voting_power > state.total_power * 2 / 3:
        return precommit_nil()
    return wait()
```

### 21.10 Pseudocode: commit and QC verification

```python
def verify_qc(qc, validator_set):
    if qc.validator_set_hash != hash_validator_set(validator_set):
        return False
    signed_power = 0
    for signer in qc.signers:
        if not verify_signature(signer, qc.sign_bytes):
            return False
        signed_power += signer.power
    return signed_power > validator_set.total_power * 2 / 3


def try_commit(block, qc, validator_set):
    if qc.block_id != block.block_id:
        return False
    if not verify_qc(qc, validator_set):
        return False
    append_block(block)
    finalize_state(block)
    return True
```

---

## 22. Slashing and evidence policy

### 22.1 Double-vote detection
If two valid signatures from the same validator exist for conflicting votes at the same height and round, the evidence is immediately reviewable for slashing.

### 22.2 Double-proposal detection
If the elected proposer signs and distributes two conflicting block proposals for the same height and round, that is slashable.

### 22.3 Evidence retention
Evidence should remain queryable for a governance-defined retention window and should itself be hash-addressable.

---

## 23. Epoch transition policy

### 23.1 Membership changes
Staking, joining, exiting, or jailing changes are staged during an epoch and activated only on epoch transition unless emergency governance says otherwise.

### 23.2 Hash commitment
Every epoch transition must commit the next validator set hash.

### 23.3 Replay protection
Votes and QCs must bind to chain ID, height, round, and active validator-set hash.

---

## 24. AIR / PoM security policy

### 24.1 Advisory-only by default
AIR and PoM outputs are non-final advisory artifacts unless a future governance document explicitly elevates any subset of their functionality.

### 24.2 Auditability
Every privileged AIR-assisted draft action should bind to:
- session ID
- nonce
- timestamp
- payload hash
- operator identity when present

### 24.3 Privacy
Raw mental-state, biometric, or device telemetry must stay off-chain. Only bounded summaries, hashes, or authorized attestation references may be attached.

---

## 25. Implementation plan

### 25.1 Suggested Rust modules
- `hash.rs`
- `types.rs`
- `encoding.rs`
- `vote.rs`
- `qc.rs`
- `validator_set.rs`
- `consensus.rs`
- `evidence.rs`
- `air.rs`

### 25.2 Suggested Python verifier tools
- canonical encoder / decoder
- hash test vector checker
- QC threshold checker
- evidence validator
- manifest / SHA-256 register tool

### 25.3 Milestones
- 2026-03-21 to 2026-04-10: canonical object and test-vector phase
- 2026-04-11 to 2026-05-10: validator loop, QC, evidence path
- 2026-05-11 to 2026-06-05: AIR boundary hardening and devnet drills
- 2026-06-06 to 2026-06-21: freeze, test-run review, manifest refresh

---

## 26. PoM Oracle Mock integration note

Internal artifact name referenced by project direction:
`NOTE-LuxeVault-PoM-Oracle-MockGenerator_v1_2026-02-20.py`

This artifact should be treated as a devnet-only mock generator unless formally reviewed and promoted. In production, any oracle or attestation service should use stronger signer management, documented privacy rules, replay protection, and explicit governance approval before interacting with consensus-adjacent workflows.

---

## 27. Closing statement

SLVR8 / Veritas v0.2-draft is currently best understood as a **stake-weighted BFT chain specification with strict separation between consensus finality and advisory AI layers**. Bitcoin supplies the historical value-transfer anchor, CometBFT supplies the practical BFT state-machine reference, and the OTFZ public whitepaper supplies the platform-level narrative into which the implementation is being organized [Source](https://bitcoin.org/bitcoin.pdf) [Source](https://docs.cometbft.com/main/spec/consensus/consensus) [Source](https://outthefreezer.square.site/whitepaper)
