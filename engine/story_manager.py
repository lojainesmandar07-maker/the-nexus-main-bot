import json
import os
from typing import Dict, Optional
from engine.models import Story, Scene, Choice, Perspective

class StoryManager:
    def __init__(self, stories_dir: str = "data/stories"):
        self.stories_dir = stories_dir
        self.stories: Dict[int, Story] = {}
        self.load_all_stories()

    def load_all_stories(self):
        if not os.path.exists(self.stories_dir):
            os.makedirs(self.stories_dir)

        for filename in os.listdir(self.stories_dir):
            if filename.endswith(".json"):
                self.load_story(os.path.join(self.stories_dir, filename))

    def load_story(self, filepath: str):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            filename = os.path.basename(filepath)

            # Check if this is the new nested format (world format)
            if "world" in data and "categories" in data:
                world_name = data["world"]
                world_type = filename.split('.')[0] # e.g. "fantasy"

                for category in data["categories"]:
                    cat_name = category.get("name")
                    for s_data in category.get("stories", []):
                        self._parse_and_add_story(s_data, theme=cat_name, world_type=world_type)
            # Check if it's the new nested solo format
            elif "id" in data and "perspectives" in data and "nodes" in data:
                 self._parse_and_add_story(data, theme="قصص-فردية", world_type="solo")
            # Old format fallback
            else:
                 self._parse_and_add_old_story(data)

        except Exception as e:
            print(f"Error loading story from {filepath}: {e}")

    def _parse_and_add_story(self, data: dict, theme: str, world_type: str):
        try:
            scenes = {}
            for node_id, node_data in data.get("nodes", {}).items():
                choices = []
                for choice_data in node_data.get("choices", []):
                    # Handle new "label" and "next" format, fallback to old "text" and "next_scene"
                    text = choice_data.get("label", choice_data.get("text", "استمرار"))
                    next_scene = choice_data.get("next", choice_data.get("next_scene", ""))
                    choices.append(Choice(
                        text=text,
                        next_scene=next_scene,
                        color=choice_data.get("color", "primary"),
                        points_reward=choice_data.get("points_reward", 0),
                        required_points=choice_data.get("required_points")
                    ))

                scenes[node_id] = Scene(
                    id=node_id,
                    title=node_id, # The new format doesn't have scene titles natively, just nodes
                    text=node_data.get("text", ""),
                    choices=choices,
                    is_ending=node_data.get("is_ending", False),
                    image_url=node_data.get("image_url")
                )

            # Extract perspectives if present
            perspectives = []
            for p_data in data.get("perspectives", []):
                 perspectives.append(Perspective(
                     id=p_data.get("id", ""),
                     label=p_data.get("label", ""),
                     emoji=p_data.get("emoji", ""),
                     description=p_data.get("description", ""),
                     start_node=p_data.get("start_node", "")
                 ))

            # Use 'id' from JSON, but ensure it's converted to an int hash if it's a string, or require int IDs.
            # Assuming prompt IDs might be strings like "story_001", we hash them or extract integers.
            raw_id = data.get("id", 0)
            if isinstance(raw_id, str):
                import hashlib
                story_id = int(hashlib.sha256(raw_id.encode()).hexdigest(), 16) % 10**8
            else:
                story_id = raw_id

            nodes = data.get("nodes", {})
            default_start = "start" if "start" in nodes else (next(iter(nodes)) if nodes else "start")
            story = Story(
                id=story_id,
                title=data.get("title", "بدون عنوان"),
                theme=theme,
                series=data.get("series", 1),
                game_mode="single", # All of these nested ones are single player for now based on prompt
                description=data.get("summary", data.get("description", "")),
                scenes=scenes,
                start_scene=default_start if not perspectives else perspectives[0].start_node, # fallback
                world_type=world_type,
                perspectives=perspectives
            )

            self.stories[story.id] = story
            print(f"Loaded Nested Story {story.id}: {story.title}")

        except Exception as e:
            print(f"Error parsing nested story {data.get('title')}: {e}")

    def _parse_and_add_old_story(self, data: dict):
        scenes = {}
        for scene_data in data.get("scenes", []):
            choices = []
            for choice_data in scene_data.get("choices", []):
                choices.append(Choice(
                    text=choice_data["text"],
                    next_scene=choice_data["next_scene"],
                    color=choice_data.get("color", "primary"),
                    points_reward=choice_data.get("points_reward", 0),
                    required_points=choice_data.get("required_points")
                ))

            scenes[scene_data["id"]] = Scene(
                id=scene_data["id"],
                title=scene_data["title"],
                text=scene_data["text"],
                choices=choices,
                is_ending=scene_data.get("is_ending", False),
                image_url=scene_data.get("image_url")
            )

        story = Story(
            id=data["id"],
            title=data["title"],
            theme=data.get("theme", "عام"),
            series=data.get("series", 1),
            game_mode=data.get("game_mode", "single"),
            description=data.get("description", ""),
            scenes=scenes,
            start_scene=data.get("start_scene", "start"),
            image_url=data.get("image_url"),
            world_type=data.get("world_type")
        )

        self.stories[story.id] = story
        print(f"Loaded Old Story {story.id}: {story.title}")

    def get_story(self, story_id: int) -> Optional[Story]:
        return self.stories.get(story_id)

    def get_all_stories(self) -> Dict[int, Story]:
        return self.stories

    def get_stories_by_mode(self, game_mode: str) -> Dict[int, Story]:
        return {k: v for k, v in self.stories.items() if v.game_mode == game_mode}
