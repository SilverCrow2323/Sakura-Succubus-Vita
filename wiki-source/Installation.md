# Install on PS Vita

This port uses the Ren'Py PSVita distribution. Install the VPK, then copy the original game's `game/` folder into the application title directory.

## Before you begin

- Download the VPK for this port.
- Obtain the original PC game from its official source: [original game page](https://store.steampowered.com/app/1202310/Sakura_Succubus).
- Extract or otherwise access the original game's `game/` folder.
- Have VitaShell available on the Vita.

> [!IMPORTANT]
> **MUST KNOW!!** The original game's data is not the same as the VPK. Keep the content folder separate and copy it into the exact title path shown below.

## Quick install with VitaShell

1. Download the VPK to your PC or device.
2. Extract the VPK like a ZIP/RAR archive into a new folder.
3. Transfer that folder to the Vita.
4. Open **VitaShell**.
5. Highlight the extracted folder without opening it.
6. Press **TRIANGLE**, open **More**, then select **Install folder**.
7. Confirm the two prompts.
8. Copy the original game's `game/` folder into:

```
ux0:/app/RNPYSS001/
```

## Verify

- Confirm the final path is `ux0:/app/RNPYSS001/game/`.
- Keep the `game` folder name intact.
- Launch the port from LiveArea.

The repository notes that installing the VPK directly may take a long time. Its documented quicker route is to extract the VPK as an archive and use VitaShell's **Install folder** command.
