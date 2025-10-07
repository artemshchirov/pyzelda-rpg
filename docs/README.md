# PyZelda RPG Documentation

## Overview

PyZelda RPG is a top-down Zelda-inspired adventure built with Python and Pygame. The project pairs a scene-based level loader with modular combat, magic, and UI systems. Maps are authored in Tiled and exported as CSV layers that are loaded at runtime.

## Architecture

### Runtime Flow

- `code/main.py` bootstraps Pygame, manages game states (`start`, `game`, `death`), and owns the `Game` loop.
- A `Level` instance keeps the active scene: it loads tile layers, spawns entities, and coordinates combat, UI, and transitions.
- Conditional menus (start, pause, death) reuse the same display surface and audio channel, keeping the loop deterministic.

### Scene Composition

- `Level.create_map` reads CSV layers from `data/map/` to build tiles, objects, interactive grass, and entity spawn points.
- Layered sprite groups inside `YSortCameraGroup` drive rendering and camera offset so the player remains centered.
- Transition markers inside the entity layer map to other maps, enabling multi-map progression without reloading the game.

### Core Systems

- **Entities & Movement**: `Entity` supplies movement, collision, and animation scaffolding consumed by `Player` and `Enemy` subclasses.
- **Combat**: `weapon.py`, `magic.py`, and `particles.py` manage melee weapons, spells, and particle effects, all orchestrated through `Level.player_attack_logic`.
- **Progression**: `upgrade.py` exposes the upgrade menu, while `save_manager.py` persists player stats and defeated enemies for continuity.
- **User Interface**: `ui.py` renders health, energy, weapon/magic slots, and matches the asset palette defined in `settings.py`.
- **Pathfinding**: `pathfinding_utils.py` builds a walkable grid and provides A* helpers for enemy navigation.

## Module Reference

| Path | Responsibilities |
| --- | --- |
| `code/main.py` | Entry point, game state management, audio bootstrapping, and scene lifecycle. |
| `code/level.py` | Scene graph, sprite group wiring, map loading, transitions, and combat orchestration. |
| `code/settings.py` | Centralized configuration for dimensions, colors, weapon/magic data, and monster stats. |
| `code/player.py` | Player controls, animations, combat actions, and serialization hooks. |
| `code/enemy.py` | Enemy behaviours, attack logic, and interaction with the player and pathfinding grid. |
| `code/entity.py` | Shared movement, collision, and animation primitives for all moving sprites. |
| `code/tile.py` | Static world tiles, grass, and object sprites with hitboxes. |
| `code/weapon.py` & `code/magic.py` | Spawn and update weapon hitboxes and magic projectiles/effects. |
| `code/ui.py` | HUD rendering, cooldown indicators, and upgrade menu slots. |
| `code/particles.py` | Reusable animation player for particles, weapon trails, and experience pickups. |
| `code/upgrade.py` | Upgrade menu layout and stat progression logic. |
| `code/pathfinding_utils.py` | Grid construction and A* helper utilities. |
| `code/support.py` | Disk path resolution and bulk import helpers for CSV maps and sprite folders. |
| `code/save_manager.py` | JSON save/load helpers for persisting player and world state. |
| `code/debug.py` | On-screen debug text helper for quick instrumentation. |

## Assets and Data

- `data/map/`: CSV layers exported from Tiled (`*_FloorBlocks`, `*_Grass`, `*_Objects`, `*_Entities`).
- `graphics/`: Sprite sheets and animation frames for tiles, characters, weapons, particles, and UI.
- `audio/`: Background music, combat SFX, spell audio, and UI cues.
- `font/`: Contains the Joystix font used for UI overlays.

## Persistence

Game progress is written to `savegame.json` via `save_manager.save_game`. The file tracks player stats, defeated enemies, and destroyed grass. Loading occurs at startup if the file exists and is well-formed.

## Development Notes

- Run the game from the repository root with `python code/main.py` after installing Pygame.
- The game window opens centered at ~60% of your desktop resolution, supports live resizing, and double-clicking the title bar promotes it to fullscreen (press F11 again to return to windowed mode).
- Tile layer CSVs must match the naming scheme `map_<map_id>_<LayerName>.csv` for `Level.create_map` to detect them.
- Use `support.get_path` when referencing assets so that relative paths resolve consistently across platforms.
- When adding systems, prefer extending existing sprite groups and managers to keep rendering and collision predictable.
- Press `ESC` in-game to open the pause overlay; use the Settings option there to toggle audio without leaving the session.
- Default audio behaviour is controlled by `IS_MUSIC_ENABLED` in `code/settings.py`. Disabling it mutes both background music and SFX until re-enabled.

## Versioning

- The active version is defined as `GAME_VERSION` in `code/settings.py`; bump this constant when shipping new player-facing behaviour or fixes.
- Document each bump at the top of `CHANGELOG.md` with the same version string, release date (`YYYY-MM-DD`), and concise bullet list of notable updates.
- Visible references such as the start screen label read from `GAME_VERSION`, so updating the constant keeps UI and documentation aligned.

## Tile & UI Authoring Guide

### Adding or Updating Tiles

1. Place new sprite sheets or single-tile images under an appropriate folder in `graphics/` (for example `graphics/objects` for props or `graphics/grass` for foliage). Keep filenames lowercase and descriptive.
2. Open the Tiled project used to author maps and import the new art into the tileset. Maintain the existing tile size (`64x64`) so hitboxes still align with `TILESIZE`.
3. Paint the updated layer and export each layer back to the repository, preserving the naming scheme `map_<map_id>_<Layer>.csv` inside `data/map/`.
4. If the new tile should block movement, ensure the value appears in the `FloorBlocks` CSV so `Level.create_map` spawns an obstacle tile. Decorative tiles can live in `Grass` or `Objects` layers.
5. Launch the game (`python code/main.py`) and walk the updated area to confirm collisions and draw order look correct.

### Updating the UI

1. Adjust HUD layout, bar thickness, or slot positions inside `code/ui.py`. The class reads constants from `code/settings.py`, so prefer tweaking them there when only values change.
2. Add new icons or fonts under `graphics/` or `font/` and reference them through `support.get_path` to keep asset paths consistent.
3. For new UI states (for example, inventory tabs), extend the `UI.display` method and reuse existing surface drawing helpers so the update loop stays lightweight.
4. After changes, run the game and trigger the relevant UI (HUD, upgrade menu, etc.) to verify positioning, scaling, and performance.
