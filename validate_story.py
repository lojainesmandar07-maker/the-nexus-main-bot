import json
from pathlib import Path

from core.category_catalog import category_names_by_mode

STORIES_DIR = Path("data/stories")


def validate(filepath: Path) -> bool:
    with filepath.open("r", encoding="utf-8") as f:
        story = json.load(f)

    scene_ids = {scene["id"] for scene in story["scenes"]}

    start_scene = story["start_scene"]
    if start_scene not in scene_ids:
        print(f"ERROR: {filepath} -> Start scene {start_scene} not found!")
        return False

    for scene in story["scenes"]:
        for choice in scene.get("choices", []):
            if choice["next_scene"] not in scene_ids:
                print(
                    f"ERROR: {filepath} -> Scene {scene['id']} references missing next_scene {choice['next_scene']}"
                )
                return False

    mode = story.get("game_mode")
    allowed_themes = set(category_names_by_mode(mode))
    theme = story.get("theme", "")
    if allowed_themes and theme not in allowed_themes:
        print(
            f"ERROR: {filepath} -> Theme '{theme}' is not valid for mode '{mode}'. "
            f"Allowed: {sorted(allowed_themes)}"
        )
        return False

    print(f"Validation passed for {filepath}. All links and theme checks are valid!")
    return True


def validate_all() -> bool:
    files = sorted(STORIES_DIR.glob("*.json"))
    if not files:
        print("No story files found.")
        return False

    all_ok = True
    for filepath in files:
        if not validate(filepath):
            all_ok = False
    return all_ok


if __name__ == "__main__":
    if not validate_all():
        raise SystemExit(1)
