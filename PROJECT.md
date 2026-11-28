# Project: Sakura Succubus — PlayStation Vita port

## Purpose
Maintain the Vita-side application metadata and LiveArea package shell for the Ren'Py conversion of Sakura Succubus. This is a port/package repository, not the source repository for the original game.

## Users and use cases
- Vita owners installing the published VPK and supplying their own legally obtained original game files.
- Maintainers checking title identity, LiveArea assets, compatibility notes and release packaging.
- Port testers recording boot, save/load, rendering, audio and performance results on real hardware.

## Scope and boundaries
In scope: Vita SFO metadata, icon/background/startup assets, installation instructions, port-specific compatibility notes and reproducibility evidence.

Out of scope: redistribution of the original game's game/ payload, DRM or license bypass, claims of upstream ownership, and changes to the Ren'Py Vita runtime itself. The project references the upstream game at https://store.steampowered.com/app/1202310/Sakura_Succubus and the Ren'Py Vita Distribution Tool by SonicMastr. A rebuild must record exact runtime/source revisions rather than assume the current upstream binary is identical.

## Target
- PlayStation Vita / PlayStation TV with a compatible homebrew environment.
- Ren'Py Vita runtime and VitaShell VPK installation.
- Vita display and controls; no desktop or Switch compatibility is implied.

## Package architecture
- sce_sys/param.sfo: Vita title metadata; expected TITLE_ID RNPYSS001.
- sce_sys/icon0.png, pic0.png and livearea/contents/: application and LiveArea presentation.
- README.md and wiki-source/: installation, source attribution and troubleshooting.
- Original game assets are supplied separately by the user at the title-specific path documented in README.md.

## Dependencies and provenance
- Original game source: https://store.steampowered.com/app/1202310/Sakura_Succubus
- Ren'Py PSVita conversion tool: https://github.com/SonicMastr/renpy-vita
- VitaShell and a compatible Vita homebrew environment.
- Rebuilds must record tool/runtime commit, input game build identifier, generated VPK hash and build environment. The repository does not establish that the original game payload is redistributable.

## Safety, accessibility and localization
- Never commit the original game's proprietary payload or user saves.
- Validate SFO offsets and lengths before reading metadata; do not treat filenames as trusted identifiers.
- Keep Markdown instructions readable and distinguish known bugs from untested behavior.
- Keep user-facing instructions in English unless a separately reviewed translation is added.

## Verified baseline
- Tracked SFO title ID: RNPYSS001; title: Sakura Succubus; app version: 1.00.
- The repository contains Vita metadata/LiveArea assets and documentation; no original game/ directory is part of the tracked package.
- Runtime boot, save/load, full playthrough and physical-device performance are not certified by metadata checks.
