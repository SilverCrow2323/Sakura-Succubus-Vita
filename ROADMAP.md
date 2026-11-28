# Roadmap — Sakura Succubus Vita

## Current verified stage
Static package-integrity validation and a repository-specific project boundary are now tracked. The CI validator checks the SFO signature, PNG headers/dimensions, LiveArea XML structure and local image references. This is a software packaging check, not a Vita boot test.

## Ordered milestones

### M1 — Reproducible package metadata
- Keep exactly one Vita `sce_sys/param.sfo` package root.
- Validate `icon0.png`, `pic0.png`, LiveArea background and startup images.
- Reject missing, malformed or path-escaping LiveArea references.
- Acceptance: `python tools/validate_vita_package.py` and the package-integrity CI job pass.

### M2 — Upstream and runtime provenance
- Record the original game/mod source, the Ren'Py Vita runtime/tool revision and any required user-supplied files.
- Confirm the SFO title ID and the documented `ux0:app/` destination from package metadata.
- Review third-party notices and do not bundle game data without redistribution permission.
- Acceptance: installation instructions, SFO identity and source/license references agree.

### M3 — Real-device integration
- Install the package with VitaShell on a real PS Vita.
- Copy only the documented original-game payload to the verified application path.
- Test first boot, a representative play segment, save/load, suspend/resume and clean exit.
- Record firmware, runtime build, device model and observed performance.
- Acceptance: a reproducible device report exists; automated CI is not substituted for this test.

### M4 — Stable package candidate
- Build the VPK from the verified package tree using the pinned Ren'Py Vita toolchain.
- Attach SHA-256 checksums and release notes describing upstream/runtime versions and known limitations.
- Acceptance: package integrity CI passes, source/license review is complete, and the M3 device report has no unresolved release-blocking issue.

## Release gate and risks
No stable release is declared until the exact app identity, runtime revision and device results are recorded. The main risks are upstream game changes, Ren'Py Vita compatibility, missing original-game files, uncertain third-party asset licenses and hardware-only runtime defects.
