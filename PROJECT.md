# Project definition — Sakura Succubus Vita

## Product and boundary
A PS Vita Ren'Py package shell for **Sakura Succubus** (the first game). It carries Vita application metadata, LiveArea assets and installation instructions; it is not the Steam game or its upstream source.

## Upstream and runtime
- Original game: [Sakura Succubus on Steam](https://store.steampowered.com/app/1202310/Sakura_Succubus).
- Runtime/tool lineage: [Ren'Py PSVita Distribution Tool](https://github.com/SonicMastr/renpy-vita).
- Users provide the original PC `game/` directory. Do not commit proprietary game data.

## Users and target
PS Vita owners installing the package through VitaShell. Firmware and runtime compatibility require physical verification.

## Install contract
The README documents the game-data destination `ux0:/app/RNPYSS001/`. The SFO title ID and install instructions must agree.

## Architecture and dependencies
Static package components: `sce_sys/param.sfo`, `icon0.png`, `pic0.png`, LiveArea XML/background/startup assets and documentation. Runtime and game data are external.

## Security and quality
Validate package identity, image headers and XML asset references. Preserve the separation between package shell and user-supplied game files. Documentation is English; no unsupported performance or firmware claims.

## Verified baseline
The repository is a package/metadata and documentation repository; the original game data is not present. CI now performs read-only structural validation. Vita installation and gameplay have not been certified by CI.

## Release acceptance
SFO and LiveArea checks pass, the correct app ID/path is documented, the upstream source is attributed, and a real Vita test covers install, boot, save/load and suspend/resume.