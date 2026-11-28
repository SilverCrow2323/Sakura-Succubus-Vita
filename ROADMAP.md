# Roadmap — Sakura Succubus Vita port

## P0 — Preserve the known package identity
- [x] Track Vita SFO metadata and LiveArea assets.
- [x] Document the original-game source and separate user-supplied game files.
- [ ] Reconcile the published VPK with tracked RNPYSS001 metadata and record its SHA-256.

## P1 — Reproducible package integrity
- [x] Add an offline SFO parser regression test with bounds checks.
- [x] Verify title ID, category, title and application version in CI.
- [x] Verify required PNG assets and parse the LiveArea XML.
- [x] Fail if an original game/ payload is accidentally committed.
- [ ] Add a reproducible build recipe pinned to the exact Ren'Py Vita runtime/tool revision.

## P2 — Runtime qualification
- [ ] Install the VPK on a physical PS Vita and record firmware, storage layout and free space.
- [ ] Verify first boot, game-file discovery, save/load, audio, suspend/resume and repeated launch.
- [ ] Record title-specific rendering/performance issues with reproducible save points.

## P3 — Maintenance release
- [ ] Rebuild only from a documented input game build and pinned runtime.
- [ ] Compare generated package metadata and asset hashes against the reviewed baseline.
- [ ] Publish release notes and checksums only after physical-device qualification.

## Acceptance criteria
A package update is ready for review when CI passes, the SFO identity remains RNPYSS001, no original game payload is present, all required LiveArea assets are valid, and the release candidate has a separately recorded physical Vita test report. CI alone is not hardware certification.

## Current release target
Maintain the existing published port version 1.00; this documentation/test change does not propose a release or version bump.
