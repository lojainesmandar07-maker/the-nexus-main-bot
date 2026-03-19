import json
import os
from typing import Dict, Optional
from engine.models import Story, Scene, Choice

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
                image_url=data.get("image_url")
            )

            self.stories[story.id] = story
            print(f"Loaded Story {story.id}: {story.title}")

        except Exception as e:
            print(f"Error loading story from {filepath}: {e}")

    def get_story(self, story_id: int) -> Optional[Story]:
        return self.stories.get(story_id)

    def get_all_stories(self) -> Dict[int, Story]:
        return self.stories

    def get_stories_by_mode(self, game_mode: str) -> Dict[int, Story]:
        return {k: v for k, v in self.stories.items() if v.game_mode == game_mode}
