# Python ⚔ PyZelda RPG ⚔ Pygame

A Zelda style game in Python and Pygame.\
This includes weapons and enemies, magic and spells, upgrades, and sound effects.\
Maps are authored in Tiled and exported as CSV layers that load at runtime.\
The game was created following [Clear Code's tutorial](https://www.youtube.com/watch?v=QU1pPzEGrqw) and expanded with save/load support, particles, and multi-map transitions.

![image_2022-11-28_01-22-10](https://user-images.githubusercontent.com/78075439/204165230-b9c48243-f1b8-4906-8088-5a5233865587.png)

## Run Project Locally

```bash
git clone https://github.com/artemshchirov/pyzelda-rpg.git
cd pyzelda-rpg
python -m pip install pygame
python code/main.py
```

## TODO

- [x] Level setup
- [x] Creating the player
- [x] Creating the camera
- [x] Graphics
- [x] Player animations
- [x] Weapons
- [x] UI
- [x] Magic setup
- [x] Enemy creation
- [x] Player-enemy interaction
- [x] Particles
- [x] Spells
- [x] Upgrade system and menu
- [x] Audio
- [x] Save / Load game
- [x] Exp animation
- [ ] Over world
- [ ] Enemy pathfinder

## Architecture Overview

- `code/main.py` boots Pygame, manages high-level game states (`start`, `game`, `death`), and drives the main loop.
- `Level` coordinates the active scene: it loads map layers, spawns tiles and entities, resolves combat, and triggers map transitions.
- Rendering uses `YSortCameraGroup` to keep sprites ordered by `rect.centery` while the player stays centered on screen.
- Menus, audio, and particles reuse the same display surface, keeping update cadence deterministic.

## Module Reference

| Path | Responsibilities |
| --- | --- |
| `code/main.py` | Entry point, game state management, audio bootstrapping, and scene lifecycle. |
| `code/level.py` | Scene graph, sprite group wiring, CSV map loading, transitions, and combat orchestration. |
| `code/settings.py` | Display constants, color palette, weapon/magic configuration, and monster stats. |
| `code/player.py` | Player input, movement, combat actions, animations, and serialization hooks. |
| `code/enemy.py` | Enemy behaviours, attack logic, and interactions driven by optional pathfinding. |
| `code/entity.py` | Shared movement, collision, and animation primitives for movable sprites. |
| `code/tile.py` | Static world tiles, grass, and object sprites with hitboxes. |
| `code/weapon.py` / `code/magic.py` | Spawn and update weapon hitboxes and magical effects. |
| `code/ui.py` | HUD rendering, cooldown indicators, upgrade overlay. |
| `code/particles.py` | Animation player for particles, weapon trails, and experience pickups. |
| `code/upgrade.py` | Upgrade menu layout and stat progression logic. |
| `code/pathfinding_utils.py` | Grid construction and A* helper utilities for movement planning. |
| `code/support.py` | Asset path resolution and helpers for CSV and folder imports. |
| `code/save_manager.py` | JSON save/load helpers for persisting player and world state. |
| `code/debug.py` | On-screen debug text helper for quick instrumentation. |

## Assets and Data

- `data/map/`: CSV layers exported from Tiled (`map_<map_id>_<Layer>.csv`).
- `graphics/`: Sprite sheets and animation frames for tiles, characters, weapons, particles, and UI.
- `audio/`: Background music, combat SFX, spell audio, and UI cues.
- `font/`: Contains the Joystix font used for UI overlays.

## Persistence

Game progress is saved to `savegame.json` via `save_manager.save_game`, tracking player stats, defeated enemies, and destroyed grass. A valid file is loaded automatically on startup.

## Development Notes

- Run the game from the repository root so `support.get_path` can resolve relative assets.
- Tile layer CSVs must follow the naming convention `map_<map_id>_<LayerName>.csv`.
- Reuse existing sprite groups and managers when extending gameplay so rendering, collisions, and UI stay in sync.
- Press `ESC` while playing to open the pause menu (Resume / Settings). The Settings panel allows toggling audio via `IS_MUSIC_ENABLED` in `code/settings.py`.
