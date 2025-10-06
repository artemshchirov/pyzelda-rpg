# AI Agents Guide (PyZelda RPG)

This repository runs on Python and Pygame. Always operate from the workspace root so asset-relative paths resolve correctly.

## Project Structure

- `code/`: Gameplay source (entry point, level management, entities, combat systems).
- `data/`: Tiled CSV exports that describe world geometry and entity placement.
- `graphics/`: Sprite sheets, animation frames, UI assets, and tilemaps.
- `audio/`: Music, ambient, combat, and UI sounds.
- `font/`: Bundled fonts for in-game UI.
- `docs/`: Project documentation for architecture and agent workflow.

## Prerequisites

- Python 3.9+ with `pip` available on PATH.
- Install dependencies once at the root: `python -m pip install pygame`. Reuse existing virtual environments when possible; the project does not rely on external native packages beyond SDL dependencies bundled with Pygame.
- Avoid `pip install` in subfolders; asset loaders assume relative paths from the repository root.

## Runtime Basics

- Launch the game loop with `python code/main.py`. The game starts in a menu state and transitions into the active `Level` once "Start" is selected.
- Save data persists to `savegame.json` in the root directory. Delete the file when you need a clean slate.
- When editing map CSVs, keep layer names aligned with `Level.create_map` expectations (`map_<map_id>_<Layer>.csv`).
- Hit `ESC` during gameplay to open the pause overlay (Resume / Settings). Toggle audio from there; the default flag lives at `code/settings.py::IS_MUSIC_ENABLED`.

## Day-to-Day Commands

- `python code/main.py` — run the full game.
- `python code/main.py --debug` is not implemented; instrument debug output via `code/debug.py` or temporary logs when needed.
- `python -m compileall code` — optional sanity check to ensure Python syntax validity before handoff.

## Coding Standards

- Pure Python; follow existing patterns in `code/` and keep diffs surgical.
- Use `support.get_path` for filesystem access to maintain cross-platform compatibility.
- Keep sprite groups and update loops lightweight; prefer reusing managers like `Level.visible_sprites` instead of creating new global state.
- Comment only when logic is non-obvious; align wording with existing documentation tone.

## Assistant Workflow

- Run commands from the repository root; relative imports break if executed elsewhere.
- Playtest after gameplay-affecting changes. Automated tests are absent, so short manual verification sessions are the norm.
- After modifying data assets, confirm they load by starting the game and traversing affected areas.
- Reference `/README.md` and `docs/README.md` for architecture context before making structural changes.

## Documentation

- Keep new docs in `docs/` and update `docs/README.md` when architecture changes.
- Summarize agent-facing workflows here so future automation can ramp quickly.
