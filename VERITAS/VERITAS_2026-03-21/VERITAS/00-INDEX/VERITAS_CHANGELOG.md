# VERITAS Changelog

Version line: v0.2-draft  
Launch date: 2026-03-21  
Target run date: 2026-06-21

---

## 2026-03-21 — Core pack completed and bundled

### Added
- `00-INDEX/VERITAS_MASTER_INDEX.md`
- `00-INDEX/VERITAS_CHANGELOG.md`
- `00-INDEX/VERITAS_FILE_REGISTER.csv`
- `00-INDEX/VERITAS_TAGS.json`
- `00-INDEX/Public_Source_Links.md`
- `03-CONSENSUS/SLVR8_Veritas_Spec_v0_2.md`
- `06-BUSINESS/Multi-Commerce_MCt_Unreleased_Token_Profile.md`

### Confirmed in bundle
- `01-WHITEPAPER/EchoMind_Overview.md`
- `01-WHITEPAPER/Spektraxa_AIR_Identity.md`
- `01-WHITEPAPER/Homepage_Hero_Copy.md`
- `05-EDUCATION/Digital_Assets_Explained.md`
- `05-EDUCATION/AIR_Onboarding_Script.md`
- `06-BUSINESS/Investor_One_Pager.md`
- `README.md`

### Content highlights
- Consolidated the Veritas / SLVR8 consensus draft into a single spec file with wire format guidance, pseudocode, epoch rules, and AIR / PoM boundary language.
- Added index and source tracking files to support future SHA-256 manifesting and ingest workflows.
- Added a separate restricted file for the unrevealed unreleased **Multi-Commerce (MCt)** token using the project specifications provided internally on 2026-03-21.

### Source anchors used across the pack
The current content line is grounded in the public OUTTHEFREEZER ecosystem presentation, the whitepaper’s Veritas / SLVR8 positioning, Bitcoin’s peer-to-peer cash framing, and CometBFT’s round-based BFT consensus structure [Source](https://outthefreezer.shop/) [Source](https://outthefreezer.square.site/whitepaper) [Source](https://bitcoin.org/bitcoin.pdf) [Source](https://docs.cometbft.com/main/spec/consensus/consensus)

---

## Planned next update window

### Between 2026-03-22 and 2026-04-10
- add formal test vectors for SLVR8 hashing
- add validator-set examples and sample QC bitmaps
- add a PoM mock integration appendix for devnet use

### Between 2026-04-11 and 2026-05-10
- expand evidence and slashing cases
- add wire examples for AIR session and request payloads
- prepare implementation notes for Rust modules and Python verifier harness

### Between 2026-05-11 and 2026-06-05
- freeze v0.2 wording for devnet / test-run usage
- refresh hashes and manifest
- prepare investor and operator presentation pack revisions

### By 2026-06-21
- complete v0.2 run target review
- publish updated manifest, changelog, and ready-state checklist
